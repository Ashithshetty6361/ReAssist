"""
Root Agent - Orchestrates the multi-agent research pipeline
Single Responsibility: Agent coordination and pipeline execution ONLY
NO business logic, NO summarization, NO analysis
"""

import os
import time
from dotenv import load_dotenv
from agents.search_agent import create_search_agent
from agents.summarize_agent import create_summarizer_agent
from agents.synthesize_agent import create_synthesizer_agent
from agents.gap_finder_agent import create_gap_finder_agent
from agents.idea_generator_agent import create_idea_generator_agent
from agents.technique_agent import create_technique_agent
from agents.guidance_agent import create_guidance_agent
from utils.logger import get_logger, reset_logger

# Load environment variables
load_dotenv()


class RootAgent:
    """
    Root Orchestrator Agent
    Coordinates the execution of specialized agents in the research pipeline
    
    RESPONSIBILITIES:
    - Control execution order
    - Pass outputs explicitly between agents 
    - Measure latency per agent
    - Trigger logging
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
        
        # Initialize all 7 agents
        self.search_agent = create_search_agent(max_papers=max_papers)
        self.summarizer_agent = create_summarizer_agent(model=model)
        self.synthesizer_agent = create_synthesizer_agent(model=model)
        self.gap_finder_agent = create_gap_finder_agent(model=model)
        self.idea_generator_agent = create_idea_generator_agent(model=model)
        self.technique_agent = create_technique_agent(model=model)
        self.guidance_agent = create_guidance_agent(model=model)
        
        self.logger.logger.info("Root Agent initialized with 7 agents")
    
    def _slice_context(self, state, agent):
        """Strict context slicing: pass only required inputs to agent"""
        return {k: state[k] for k in agent.required_inputs if k in state}
    
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
        self.logger.logger.info("STARTING 7-AGENT RESEARCH PIPELINE (QUERY MODE)")
        self.logger.logger.info("=" * 80)
        
        results = {
            'query': query,
            'papers': [],
            'synthesis': None,
            'gaps': None,
            'ideas': None,
            'techniques': None,
            'guidance': None,
            'error': None,
            'agent_timings': {}
        }
        
        try:
            # STAGE 1/7: Search for papers
            self.logger.logger.info("\n[STAGE 1/7] Searching for relevant papers...")
            start_time = time.time()
            # Strict context slicing
            search_input = {'query': query}  # Query not in state yet
            search_result = self.search_agent.run(search_input)
            self.agent_timings['search'] = time.time() - start_time
            
            if not search_result['success'] or not search_result['papers']:
                self.logger.log_error("No papers found. Pipeline terminated.")
                results['error'] = search_result.get('error', 'No papers found')
                return results
            
            results['papers'] = search_result['papers']
            self.logger.log_papers_found(len(results['papers']))
            self.logger.logger.info(f"✓ Found {len(results['papers'])} papers ({self.agent_timings['search']:.2f}s)")
            
            # STAGE 2/7: Summarize papers
            self.logger.logger.info("\n[STAGE 2/7] Summarizing papers...")
            start_time = time.time()
            # Strict context slicing
            summarize_result = self.summarizer_agent.run(self._slice_context(results, self.summarizer_agent))
            self.agent_timings['summarizer'] = time.time() - start_time
            
            if not summarize_result['success']:
                results['error'] = summarize_result.get('error')
                return results
            
            results['papers'] = summarize_result['papers']
            self.logger.logger.info(f"✓ Summarized {len(results['papers'])} papers ({self.agent_timings['summarizer']:.2f}s)")
            
            # STAGE 3/7: Synthesize knowledge
            self.logger.logger.info("\n[STAGE 3/7] Synthesizing knowledge across papers...")
            start_time = time.time()
            # Strict context slicing
            synthesis_result = self.synthesizer_agent.run(self._slice_context(results, self.synthesizer_agent))
            self.agent_timings['synthesizer'] = time.time() - start_time
            
            if not synthesis_result['success']:
                results['error'] = synthesis_result.get('error')
                return results
            
            results['synthesis'] = synthesis_result['synthesis']
            self.logger.logger.info(f"✓ Synthesis complete ({self.agent_timings['synthesizer']:.2f}s)")
            
            # STAGE 4/7: Find research gaps
            self.logger.logger.info("\n[STAGE 4/7] Identifying research gaps...")
            start_time = time.time()
            # Strict context slicing
            gaps_result = self.gap_finder_agent.run(self._slice_context(results, self.gap_finder_agent))
            self.agent_timings['gap_finder'] = time.time() - start_time
            
            if not gaps_result['success']:
                results['error'] = gaps_result.get('error')
                return results
            
            results['gaps'] = gaps_result['gaps']
            self.logger.logger.info(f"✓ Gaps identified ({self.agent_timings['gap_finder']:.2f}s)")
            
            # STAGE 5/7: Generate research ideas
            self.logger.logger.info("\n[STAGE 5/7] Generating novel research ideas...")
            start_time = time.time()
            # Strict context slicing
            ideas_result = self.idea_generator_agent.run(self._slice_context(results, self.idea_generator_agent))
            self.agent_timings['idea_generator'] = time.time() - start_time
            
            if not ideas_result['success']:
                results['error'] = ideas_result.get('error')
                return results
            
            results['ideas'] = ideas_result['ideas']
            self.logger.logger.info(f"✓ {ideas_result['idea_count']} ideas generated ({self.agent_timings['idea_generator']:.2f}s)")
            
            # STAGE 6/7: Suggest alternative techniques
            self.logger.logger.info("\n[STAGE 6/7] Suggesting alternative techniques...")
            start_time = time.time()
            # Strict context slicing
            technique_result = self.technique_agent.run(self._slice_context(results, self.technique_agent))
            self.agent_timings['technique'] = time.time() - start_time
            
            if not technique_result['success']:
                results['error'] = technique_result.get('error')
                return results
            
            results['techniques'] = technique_result['techniques']
            self.logger.logger.info(f"✓ Techniques suggested ({self.agent_timings['technique']:.2f}s)")
            
            # STAGE 7/7: Provide research guidance
            self.logger.logger.info("\n[STAGE 7/7] Providing research guidance...")
            start_time = time.time()
            # Strict context slicing
            guidance_result = self.guidance_agent.run(self._slice_context(results, self.guidance_agent))
            self.agent_timings['guidance'] = time.time() - start_time
            
            if not guidance_result['success']:
                results['error'] = guidance_result.get('error')
                return results
            
            results['guidance'] = guidance_result['guidance']
            self.logger.logger.info(f"✓ Guidance provided ({self.agent_timings['guidance']:.2f}s)")
            
            # Pipeline completed
            total_time = sum(self.agent_timings.values())
            results['agent_timings'] = self.agent_timings
            
            self.logger.logger.info("\n" + "=" * 80)
            self.logger.logger.info(f"7-AGENT PIPELINE COMPLETED (Total: {total_time:.2f}s)")
            self.logger.logger.info("=" * 80)
            
            # Log agent timings
            for agent_name, duration in self.agent_timings.items():
                self.logger.logger.info(f"  {agent_name}: {duration:.2f}s")
            
            # Save structured log
            self.logger.save_json_log()
            
        except Exception as e:
            self.logger.log_error(f"Pipeline failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _execute_pdf_mode(self, pdf_path):
        """Execute pipeline starting with PDF upload (single paper mode)"""
        from utils.pdf_parser import extract_text_from_pdf, create_paper_dict_from_pdf
        
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("STARTING 7-AGENT RESEARCH PIPELINE (PDF UPLOAD MODE)")
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
            'error': None,
            'agent_timings': {}
        }
        
        try:
            # STAGE 0: Extract PDF text
            self.logger.logger.info("\n[STAGE 0/7] Extracting text from PDF...")
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
            self.logger.logger.info(f"✓ Extracted {pdf_extract['page_count']} pages ({self.agent_timings['pdf_extraction']:.2f}s)")
            self.logger.logger.info(f"  Title: {paper['title']}")
            
            # STAGE 1/7: Summarize paper (SKIPPING search agent)
            self.logger.logger.info("\n[STAGE 1/7] Summarizing uploaded paper...")
            start_time = time.time()
            summarize_result = self.summarizer_agent.run({'papers': results['papers']})
            self.agent_timings['summarizer'] = time.time() - start_time
            
            if not summarize_result['success']:
                results['error'] = summarize_result.get('error')
                return results
            
            results['papers'] = summarize_result['papers']
            self.logger.logger.info(f"✓ Paper summarized ({self.agent_timings['summarizer']:.2f}s)")
            
            # STAGE 2/7: Synthesize (for single paper = extract key insights)
            self.logger.logger.info("\n[STAGE 2/7] Extracting key insights...")
            start_time = time.time()
            synthesis_result = self.synthesizer_agent.run({'papers': results['papers']})
            self.agent_timings['synthesizer'] = time.time() - start_time
            
            if not synthesis_result['success']:
                results['error'] = synthesis_result.get('error')
                return results
            
            results['synthesis'] = synthesis_result['synthesis']
            self.logger.logger.info(f"✓ Insights extracted ({self.agent_timings['synthesizer']:.2f}s)")
            
            # STAGE 3/7: Find gaps/limitations/drawbacks
            self.logger.logger.info("\n[STAGE 3/7] Identifying limitations and gaps...")
            start_time = time.time()
            gaps_result = self.gap_finder_agent.run({'synthesis': results['synthesis']})
            self.agent_timings['gap_finder'] = time.time() - start_time
            
            if not gaps_result['success']:
                results['error'] = gaps_result.get('error')
                return results
            
            results['gaps'] = gaps_result['gaps']
            self.logger.logger.info(f"✓ Limitations identified ({self.agent_timings['gap_finder']:.2f}s)")
            
            # STAGE 4/7: Generate novelty opportunities
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
            self.logger.logger.info(f"✓ {ideas_result['idea_count']} opportunities generated ({self.agent_timings['idea_generator']:.2f}s)")
            
            # STAGE 5/7: Suggest alternative techniques
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
            self.logger.logger.info(f"✓ Techniques suggested ({self.agent_timings['technique']:.2f}s)")
            
            # STAGE 6/7: Provide guidance
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
            self.logger.logger.info(f"✓ Guidance provided ({self.agent_timings['guidance']:.2f}s)")
            
            # Pipeline completed
            total_time = sum(self.agent_timings.values())
            results['agent_timings'] = self.agent_timings
            
            self.logger.logger.info("\n" + "=" * 80)
            self.logger.logger.info(f"PDF ANALYSIS COMPLETED (Total: {total_time:.2f}s)")
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
