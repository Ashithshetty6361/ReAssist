"""
Root Agent - Orchestrates the multi-agent research pipeline
Single Responsibility: Agent coordination and pipeline execution ONLY
NO business logic, NO summarization, NO analysis

Pipeline now includes:
- Retrieval grading (papers scored for relevance)
- Query rewriting with retry loops (auto-fix bad queries)
- Answer verification (hallucination detection)
- Web search fallback (Tavily, when paper search fails)
"""

import os
import time
import openai
from dotenv import load_dotenv
from agents.search_agent import create_search_agent
from agents.summarize_agent import create_summarizer_agent
from agents.synthesize_agent import create_synthesizer_agent
from agents.gap_finder_agent import create_gap_finder_agent
from agents.idea_generator_agent import create_idea_generator_agent
from agents.technique_agent import create_technique_agent
from agents.guidance_agent import create_guidance_agent
# NEW: Adaptive-Rag inspired agents
from agents.relevance_grader import create_relevance_grader
from agents.query_rewriter import create_query_rewriter
from agents.answer_verifier import create_answer_verifier
from agents.web_search_agent import create_web_search_agent
from config import RELEVANCE_THRESHOLD, MAX_QUERY_REWRITES, VERIFICATION_CONFIDENCE, GRADER_MODEL
from utils.logger import get_logger, reset_logger

# Load environment variables
load_dotenv()


class PipelineError(Exception):
    """Raised when a pipeline stage fails after all retries"""
    pass


class RootAgent:
    """
    Root Orchestrator Agent
    Coordinates the execution of specialized agents in the research pipeline
    
    RESPONSIBILITIES:
    - Control execution order
    - Pass outputs explicitly between agents 
    - Measure latency per agent
    - Trigger logging
    - Manage retrieval quality loops (grade → rewrite → retry)
    - Run answer verification
    - NO business logic
    """
    
    def __init__(self, model="gpt-3.5-turbo", max_papers=5):
        """
        Initialize Root Agent
        
        Args:
            model: OpenAI model to use for LLM-based agents
            max_papers: Maximum number of papers to search for
        """
        self.model = model
        self.max_papers = max_papers
        self.logger = reset_logger()  # Create fresh logger for new session
        self.agent_timings = {}
        
        # Initialize core 7 agents
        self.search_agent = create_search_agent(max_papers=max_papers)
        self.summarizer_agent = create_summarizer_agent(model=model)
        self.synthesizer_agent = create_synthesizer_agent(model=model)
        self.gap_finder_agent = create_gap_finder_agent(model=model)
        self.idea_generator_agent = create_idea_generator_agent(model=model)
        self.technique_agent = create_technique_agent(model=model)
        self.guidance_agent = create_guidance_agent(model=model)
        
        # Initialize NEW quality-assurance agents
        self.relevance_grader = create_relevance_grader(model=GRADER_MODEL)
        self.query_rewriter = create_query_rewriter(model=GRADER_MODEL)
        self.answer_verifier = create_answer_verifier(model=GRADER_MODEL)
        self.web_search_agent = create_web_search_agent()
        
        self.logger.logger.info("Root Agent initialized with 7 core + 4 QA agents (11 total)")

    def _run_agent_with_retry(self, agent, agent_name, input_data, max_retries=2):
        """
        Run an agent with automatic retry on failure.
        Retries up to max_retries times with 2 second wait between attempts.
        Raises PipelineError if all attempts fail.
        """
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = agent.run(input_data)
                if attempt > 0:
                    self.logger.logger.info(
                        f"✓ {agent_name} succeeded on attempt {attempt + 1}"
                    )
                return result
            except Exception as e:
                last_error = e
                self.logger.logger.warning(
                    f"⚠️  {agent_name} attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt < max_retries:
                    import openai
                    if isinstance(last_error, openai.RateLimitError):
                        wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                        self.logger.logger.warning(
                            f"   Rate limit hit. Waiting {wait_time}s before retry..."
                        )
                        time.sleep(wait_time)
                    elif isinstance(last_error, openai.APIConnectionError):
                        self.logger.logger.warning("   Connection error. Waiting 3s...")
                        time.sleep(3)
                    else:
                        time.sleep(2)
        raise PipelineError(
            f"Agent '{agent_name}' failed after {max_retries + 1} attempts. "
            f"Last error: {str(last_error)}"
        )
    
    def _slice_context(self, state, agent):
        """Strict context slicing: pass only required inputs to agent"""
        return {k: state[k] for k in agent.required_inputs if k in state}
    
    def _search_with_quality_loop(self, query, results):
        """
        NEW: Search → Grade → (Rewrite → Retry) loop
        
        Flow:
        1. Search for papers
        2. Grade each paper's relevance
        3. If enough relevant papers → proceed
        4. If not enough → rewrite query → retry (up to MAX_QUERY_REWRITES times)
        5. If still not enough → web search fallback
        """
        current_query = query
        all_papers = []
        
        for rewrite_attempt in range(MAX_QUERY_REWRITES + 1):
            is_rewrite = rewrite_attempt > 0
            prefix = f"[Rewrite {rewrite_attempt}] " if is_rewrite else ""
            
            # STEP 1: Search
            self.logger.logger.info(
                f"\n  {prefix}Searching with query: '{current_query[:80]}...'"
            )
            start_time = time.time()
            search_input = {'query': current_query}
            search_result = self._run_agent_with_retry(
                self.search_agent, 'SearchAgent', search_input
            )
            search_time = time.time() - start_time
            
            if not is_rewrite:
                self.agent_timings['search'] = search_time
            else:
                self.agent_timings[f'search_rewrite_{rewrite_attempt}'] = search_time
            
            if not search_result['success'] or not search_result['papers']:
                self.logger.logger.warning(
                    f"  {prefix}Search returned no papers"
                )
                if rewrite_attempt < MAX_QUERY_REWRITES:
                    # Rewrite and retry
                    current_query = self._rewrite_query(current_query, rewrite_attempt)
                    continue
                else:
                    break
            
            # STEP 2: Grade each paper
            self.logger.logger.info(
                f"  {prefix}Grading {len(search_result['papers'])} papers for relevance..."
            )
            start_time = time.time()
            grade_result = self.relevance_grader.run({
                'papers': search_result['papers'],
                'query': query  # Always grade against ORIGINAL query
            })
            self.agent_timings[f'grading{"_r" + str(rewrite_attempt) if is_rewrite else ""}'] = time.time() - start_time
            
            if grade_result['success']:
                self.logger.logger.info(
                    f"  {prefix}✓ Grading: {grade_result['relevant_count']} relevant, "
                    f"{grade_result['dropped_count']} dropped"
                )
                if grade_result['dropped_count'] > 0:
                    self.logger.logger.info(
                        f"    Dropped: {', '.join(grade_result.get('dropped_titles', []))}"
                    )
                
                all_papers.extend(grade_result['papers'])
                
                # Deduplicate by title
                seen_titles = set()
                unique_papers = []
                for p in all_papers:
                    title = p.get('title', '')
                    if title not in seen_titles:
                        seen_titles.add(title)
                        unique_papers.append(p)
                all_papers = unique_papers
                
                if len(all_papers) >= RELEVANCE_THRESHOLD:
                    self.logger.logger.info(
                        f"  ✓ {len(all_papers)} relevant papers found — threshold met"
                    )
                    results['papers'] = all_papers
                    results['retrieval_quality'] = {
                        'relevant_count': len(all_papers),
                        'rewrites_needed': rewrite_attempt,
                        'web_fallback_used': False
                    }
                    return True
            
            # Not enough papers — rewrite if we have attempts left
            if rewrite_attempt < MAX_QUERY_REWRITES:
                self.logger.logger.warning(
                    f"  Only {len(all_papers)} relevant papers — rewriting query..."
                )
                current_query = self._rewrite_query(current_query, rewrite_attempt)
            else:
                self.logger.logger.warning(
                    f"  Max rewrites ({MAX_QUERY_REWRITES}) exhausted with {len(all_papers)} papers"
                )
        
        # STEP 3: Web search fallback
        self.logger.logger.info(
            "\n  🌐 Falling back to web search (Tavily)..."
        )
        start_time = time.time()
        web_result = self.web_search_agent.run({'query': query})
        self.agent_timings['web_search_fallback'] = time.time() - start_time
        
        if web_result['success'] and web_result['papers']:
            self.logger.logger.info(
                f"  ✓ Web search returned {web_result['count']} results"
            )
            all_papers.extend(web_result['papers'])
        else:
            self.logger.logger.warning(
                f"  ⚠️  Web search failed: {web_result.get('error', 'Unknown')}"
            )
        
        if all_papers:
            results['papers'] = all_papers
            results['retrieval_quality'] = {
                'relevant_count': len(all_papers),
                'rewrites_needed': MAX_QUERY_REWRITES,
                'web_fallback_used': True
            }
            return True
        
        self.logger.logger.error("  ✗ No papers found from any source")
        results['error'] = 'No papers found after search, rewrite, and web fallback'
        return False
    
    def _rewrite_query(self, query, attempt):
        """Rewrite a query using the QueryRewriter agent"""
        start_time = time.time()
        rewrite_result = self.query_rewriter.run({'query': query})
        self.agent_timings[f'rewrite_{attempt}'] = time.time() - start_time
        
        if rewrite_result['success']:
            new_query = rewrite_result['rewritten_query']
            self.logger.logger.info(
                f"    Rewritten: '{query[:50]}...' → '{new_query[:50]}...'"
            )
            return new_query
        else:
            self.logger.logger.warning("    Rewrite failed, using original query")
            return query
    
    def _verify_synthesis(self, results):
        """
        NEW: Run answer verification after pipeline completes.
        Adds verification metadata but does NOT block the response.
        """
        self.logger.logger.info("\n[VERIFICATION] Checking synthesis faithfulness...")
        start_time = time.time()
        
        verify_input = {
            'synthesis': results.get('synthesis', ''),
            'papers': results.get('papers', []),
            'gaps': results.get('gaps', '')
        }
        
        verify_result = self.answer_verifier.run(verify_input)
        self.agent_timings['verification'] = time.time() - start_time
        
        results['verification'] = {
            'faithful': verify_result.get('faithful', True),
            'confidence': verify_result.get('confidence', 0.0),
            'unsupported_claims': verify_result.get('unsupported_claims', []),
            'summary': verify_result.get('verification_summary', ''),
        }
        
        if verify_result.get('faithful', True):
            self.logger.logger.info(
                f"  ✓ Synthesis verified as faithful "
                f"(confidence: {verify_result.get('confidence', 0):.0%})"
            )
        else:
            claim_count = len(verify_result.get('unsupported_claims', []))
            self.logger.logger.warning(
                f"  ⚠️  Synthesis has {claim_count} unsupported claim(s) "
                f"(confidence: {verify_result.get('confidence', 0):.0%})"
            )
            for claim in verify_result.get('unsupported_claims', []):
                self.logger.logger.warning(f"    • {claim}")
    
    def execute_pipeline(self, query=None, pdf_path=None):
        """
        Execute the complete multi-agent research pipeline
        Supports TWO entry modes:
        1. Query mode: Search papers → analyze
        2. PDF mode: Upload paper → analyze
        
        Args:
            query: Research topic (for query mode)
            pdf_path: Path to PDF file (for PDF mode)
        
        Returns:
            Dictionary containing all results from the pipeline
        """
        # Detect mode
        if pdf_path:
            return self._execute_pdf_mode(pdf_path)
        elif query:
            return self._execute_query_mode(query)
        else:
            return {
                'error': 'Must provide either query or pdf_path',
                'success': False
            }
    
    def _execute_query_mode(self, query):
        """Execute pipeline starting with search (normal mode)"""
        self.logger.log_query(query)
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("STARTING ADAPTIVE RESEARCH PIPELINE (QUERY MODE)")
        self.logger.logger.info("=" * 80)
        
        results = {
            'query': query,
            'papers': [],
            'synthesis': None,
            'gaps': None,
            'ideas': None,
            'techniques': None,
            'guidance': None,
            'verification': None,
            'retrieval_quality': None,
            'error': None,
            'agent_timings': {}
        }
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # STAGE 1: SEARCH + GRADE + REWRITE LOOP (Adaptive-Rag inspired)
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 1] Search → Grade → Rewrite Loop"
            )
            
            if not self._search_with_quality_loop(query, results):
                return results
            
            self.logger.log_papers_found(len(results['papers']))
            self.logger.logger.info(
                f"✓ Retrieved {len(results['papers'])} quality-verified papers"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 2: SUMMARIZE
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info("\n[STAGE 2/8] Summarizing papers...")
            start_time = time.time()
            summarize_result = self.summarizer_agent.run(
                self._slice_context(results, self.summarizer_agent)
            )
            self.agent_timings['summarizer'] = time.time() - start_time
            
            if not summarize_result['success']:
                results['error'] = summarize_result.get('error')
                return results
            
            results['papers'] = summarize_result['papers']
            self.logger.logger.info(
                f"✓ Summarized {len(results['papers'])} papers "
                f"({self.agent_timings['summarizer']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 3: SYNTHESIZE
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 3/8] Synthesizing knowledge across papers..."
            )
            start_time = time.time()
            synthesis_result = self.synthesizer_agent.run(
                self._slice_context(results, self.synthesizer_agent)
            )
            self.agent_timings['synthesizer'] = time.time() - start_time
            
            if not synthesis_result['success']:
                results['error'] = synthesis_result.get('error')
                return results
            
            results['synthesis'] = synthesis_result['synthesis']
            self.logger.logger.info(
                f"✓ Synthesis complete ({self.agent_timings['synthesizer']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 4: FIND GAPS
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 4/8] Identifying research gaps..."
            )
            start_time = time.time()
            gaps_result = self.gap_finder_agent.run(
                self._slice_context(results, self.gap_finder_agent)
            )
            self.agent_timings['gap_finder'] = time.time() - start_time
            
            if not gaps_result['success']:
                results['error'] = gaps_result.get('error')
                return results
            
            results['gaps'] = gaps_result['gaps']
            self.logger.logger.info(
                f"✓ Gaps identified ({self.agent_timings['gap_finder']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 5: GENERATE IDEAS
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 5/8] Generating novel research ideas..."
            )
            start_time = time.time()
            ideas_result = self.idea_generator_agent.run(
                self._slice_context(results, self.idea_generator_agent)
            )
            self.agent_timings['idea_generator'] = time.time() - start_time
            
            if not ideas_result['success']:
                results['error'] = ideas_result.get('error')
                return results
            
            results['ideas'] = ideas_result['ideas']
            self.logger.logger.info(
                f"✓ {ideas_result['idea_count']} ideas generated "
                f"({self.agent_timings['idea_generator']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 6: SUGGEST TECHNIQUES
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 6/8] Suggesting alternative techniques..."
            )
            start_time = time.time()
            technique_result = self.technique_agent.run(
                self._slice_context(results, self.technique_agent)
            )
            self.agent_timings['technique'] = time.time() - start_time
            
            if not technique_result['success']:
                results['error'] = technique_result.get('error')
                return results
            
            results['techniques'] = technique_result['techniques']
            self.logger.logger.info(
                f"✓ Techniques suggested ({self.agent_timings['technique']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 7: PROVIDE GUIDANCE
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 7/8] Providing research guidance..."
            )
            start_time = time.time()
            guidance_result = self.guidance_agent.run(
                self._slice_context(results, self.guidance_agent)
            )
            self.agent_timings['guidance'] = time.time() - start_time
            
            if not guidance_result['success']:
                results['error'] = guidance_result.get('error')
                return results
            
            results['guidance'] = guidance_result['guidance']
            self.logger.logger.info(
                f"✓ Guidance provided ({self.agent_timings['guidance']:.2f}s)"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 8: VERIFY ANSWER (Hallucination Guard)
            # ═══════════════════════════════════════════════════════════════
            self.logger.logger.info(
                "\n[STAGE 8/8] Verifying synthesis faithfulness..."
            )
            self._verify_synthesis(results)
            
            # Pipeline completed
            total_time = sum(self.agent_timings.values())
            results['agent_timings'] = self.agent_timings
            
            self.logger.logger.info("\n" + "=" * 80)
            self.logger.logger.info(
                f"ADAPTIVE PIPELINE COMPLETED (Total: {total_time:.2f}s)"
            )
            self.logger.logger.info("=" * 80)
            
            # Log agent timings
            for agent_name, duration in self.agent_timings.items():
                self.logger.logger.info(f"  {agent_name}: {duration:.2f}s")
            
            # Save structured log
            self.logger.save_json_log()
            
        except Exception as e:
            self.logger.log_error(f"Pipeline failed: {str(e)}")
            results['error'] = str(e)
        
        # Build observability report
        results['observability'] = {
            'run_id': __import__('uuid').uuid4().hex[:8],
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'query': query,
            'total_time_seconds': round(sum(self.agent_timings.values()), 2),
            'agent_timings': {
                k: round(v, 2) for k, v in self.agent_timings.items()
            },
            'slowest_agent': max(self.agent_timings, key=self.agent_timings.get)
                if self.agent_timings else None,
            'papers_found': len(results.get('papers', [])),
            'ideas_generated': len(results.get('ideas', [])) 
                if isinstance(results.get('ideas'), list) else 0,
            'pipeline_success': results.get('error') is None,
            'retrieval_quality': results.get('retrieval_quality'),
            'verification': results.get('verification'),
        }

        # Save observability report
        import json, os
        os.makedirs("logs/runs", exist_ok=True)
        run_id = results['observability']['run_id']
        report_path = f"logs/runs/run_{run_id}.json"
        with open(report_path, 'w') as f:
            json.dump(results['observability'], f, indent=2)
        self.logger.logger.info(f"📊 Observability report: {report_path}")

        return results
    
    def _execute_pdf_mode(self, pdf_path):
        """Execute pipeline starting with PDF upload (single paper mode)"""
        from utils.pdf_parser import extract_text_from_pdf, create_paper_dict_from_pdf
        
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("STARTING ADAPTIVE PIPELINE (PDF UPLOAD MODE)")
        self.logger.logger.info("=" * 80)
        self.logger.logger.info(f"PDF: {pdf_path}")
        
        results = {
            'mode': 'pdf_upload',
            'pdf_path': pdf_path,
            'papers': [],
            'synthesis': None,
            'gaps': None,
            'ideas': None,
            'techniques': None,
            'guidance': None,
            'verification': None,
            'error': None,
            'agent_timings': {}
        }
        
        try:
            # STAGE 0: Extract PDF text
            self.logger.logger.info("\n[STAGE 0] Extracting text from PDF...")
            start_time = time.time()
            pdf_extract = extract_text_from_pdf(pdf_path)
            self.agent_timings['pdf_extraction'] = time.time() - start_time
            
            if not pdf_extract['success']:
                self.logger.log_error(f"PDF extraction failed: {pdf_extract['error']}")
                results['error'] = pdf_extract['error']
                return results
            
            # Convert to paper dict format
            paper = create_paper_dict_from_pdf(pdf_path, pdf_extract)
            results['papers'] = [paper]
            self.logger.logger.info(
                f"✓ Extracted {pdf_extract['page_count']} pages "
                f"({self.agent_timings['pdf_extraction']:.2f}s)"
            )
            self.logger.logger.info(f"  Title: {paper['title']}")
            
            # STAGE 1: Summarize (skip search — we have the paper)
            self.logger.logger.info("\n[STAGE 1/7] Summarizing uploaded paper...")
            start_time = time.time()
            summarize_result = self.summarizer_agent.run({'papers': results['papers']})
            self.agent_timings['summarizer'] = time.time() - start_time
            
            if not summarize_result['success']:
                results['error'] = summarize_result.get('error')
                return results
            
            results['papers'] = summarize_result['papers']
            self.logger.logger.info(
                f"✓ Paper summarized ({self.agent_timings['summarizer']:.2f}s)"
            )
            
            # STAGE 2: Synthesize
            self.logger.logger.info("\n[STAGE 2/7] Extracting key insights...")
            start_time = time.time()
            synthesis_result = self.synthesizer_agent.run({'papers': results['papers']})
            self.agent_timings['synthesizer'] = time.time() - start_time
            
            if not synthesis_result['success']:
                results['error'] = synthesis_result.get('error')
                return results
            
            results['synthesis'] = synthesis_result['synthesis']
            self.logger.logger.info(
                f"✓ Insights extracted ({self.agent_timings['synthesizer']:.2f}s)"
            )
            
            # STAGE 3: Find gaps
            self.logger.logger.info("\n[STAGE 3/7] Identifying limitations and gaps...")
            start_time = time.time()
            gaps_result = self.gap_finder_agent.run({'synthesis': results['synthesis']})
            self.agent_timings['gap_finder'] = time.time() - start_time
            
            if not gaps_result['success']:
                results['error'] = gaps_result.get('error')
                return results
            
            results['gaps'] = gaps_result['gaps']
            self.logger.logger.info(
                f"✓ Limitations identified ({self.agent_timings['gap_finder']:.2f}s)"
            )
            
            # STAGE 4: Generate ideas
            self.logger.logger.info("\n[STAGE 4/7] Generating novelty opportunities...")
            start_time = time.time()
            ideas_result = self.idea_generator_agent.run({
                'gaps': results['gaps'],
                'synthesis': results['synthesis']
            })
            self.agent_timings['idea_generator'] = time.time() - start_time
            
            if not ideas_result['success']:
                results['error'] = ideas_result.get('error')
                return results
            
            results['ideas'] = ideas_result['ideas']
            self.logger.logger.info(
                f"✓ {ideas_result['idea_count']} opportunities generated "
                f"({self.agent_timings['idea_generator']:.2f}s)"
            )
            
            # STAGE 5: Suggest techniques
            self.logger.logger.info("\n[STAGE 5/7] Suggesting alternative techniques...")
            start_time = time.time()
            technique_result = self.technique_agent.run({
                'synthesis': results['synthesis'],
                'ideas': results['ideas']
            })
            self.agent_timings['technique'] = time.time() - start_time
            
            if not technique_result['success']:
                results['error'] = technique_result.get('error')
                return results
            
            results['techniques'] = technique_result['techniques']
            self.logger.logger.info(
                f"✓ Techniques suggested ({self.agent_timings['technique']:.2f}s)"
            )
            
            # STAGE 6: Provide guidance
            self.logger.logger.info("\n[STAGE 6/7] Providing implementation guidance...")
            start_time = time.time()
            guidance_result = self.guidance_agent.run({
                'ideas': results['ideas'],
                'techniques': results['techniques']
            })
            self.agent_timings['guidance'] = time.time() - start_time
            
            if not guidance_result['success']:
                results['error'] = guidance_result.get('error')
                return results
            
            results['guidance'] = guidance_result['guidance']
            self.logger.logger.info(
                f"✓ Guidance provided ({self.agent_timings['guidance']:.2f}s)"
            )
            
            # STAGE 7: Verify (even for PDF mode)
            self.logger.logger.info("\n[STAGE 7/7] Verifying synthesis faithfulness...")
            self._verify_synthesis(results)
            
            # Pipeline completed
            total_time = sum(self.agent_timings.values())
            results['agent_timings'] = self.agent_timings
            
            self.logger.logger.info("\n" + "=" * 80)
            self.logger.logger.info(
                f"PDF ANALYSIS COMPLETED (Total: {total_time:.2f}s)"
            )
            self.logger.logger.info("=" * 80)
            
            # Log agent timings
            for agent_name, duration in self.agent_timings.items():
                self.logger.logger.info(f"  {agent_name}: {duration:.2f}s")
            
            # Save structured log
            self.logger.save_json_log()
            
        except Exception as e:
            self.logger.log_error(f"PDF pipeline failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def get_performance_summary(self):
        """Get summary of pipeline performance"""
        return {
            'agent_timings': self.agent_timings,
            'total_time': sum(self.agent_timings.values()),
            'log_summary': self.logger.get_log_summary()
        }


def create_root_agent(model="gpt-3.5-turbo", max_papers=5):
    """Factory function to create root agent"""
    return RootAgent(model=model, max_papers=max_papers)
