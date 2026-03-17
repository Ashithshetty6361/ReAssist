"""
Summarizer Agent - Summarizes individual research papers using chunking
Single Responsibility: Paper summarization with long context handling ONLY
"""

import os
from openai import OpenAI
from utils.helpers import chunk_text, clean_text
import asyncio
from concurrent.futures import ThreadPoolExecutor


class SummarizerAgent:
    """Agent responsible for summarizing individual papers"""
    
    # Define required inputs for context slicing
    required_inputs = ['papers']
    
    def __init__(self, model="gpt-3.5-turbo", max_chunk_tokens=2000):
        """
        Initialize Summarizer Agent
        
        Args:
            model: OpenAI model to use
            max_chunk_tokens: Maximum tokens per chunk
        """
        self.model = model
        self.max_chunk_tokens = max_chunk_tokens
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def run(self, input_data):
        papers = input_data.get('papers', [])
        if not papers:
            return {'papers': [], 'success': False, 'error': 'No papers provided'}

        async def _run_all():
            with ThreadPoolExecutor(max_workers=min(len(papers), 5)) as executor:
                tasks = [self._summarize_single_paper(p, executor) for p in papers]
                return await asyncio.gather(*tasks)

        try:
            summarized_papers = asyncio.run(_run_all())
            return {
                'papers': list(summarized_papers),
                'success': True,
                'error': None
            }
        except Exception as e:
            return {'papers': [], 'success': False, 'error': str(e)}

    async def _summarize_single_paper(self, paper, executor):
        loop = asyncio.get_event_loop()
        try:
            summary = await loop.run_in_executor(
                executor,
                self._summarize_single_paper_sync,
                paper
            )
            paper_copy = paper.copy()
            paper_copy['summary'] = summary
            return paper_copy
        except Exception as e:
            paper_copy = paper.copy()
            paper_copy['summary'] = (
                f"[Summary unavailable] {paper.get('abstract', '')[:200]}..."
            )
            return paper_copy

    def _summarize_single_paper_sync(self, paper):
        """Summarize a single paper using chunking if needed"""
        abstract = clean_text(paper.get('abstract', ''))
        
        # Chunk the abstract if it's too long
        chunks = chunk_text(abstract, max_tokens=self.max_chunk_tokens, model=self.model)
        
        if len(chunks) == 1:
            return self._summarize_chunk(chunks[0], paper['title'])
        else:
            # Multiple chunks - summarize each and combine
            chunk_summaries = []
            for chunk in chunks:
                chunk_summary = self._summarize_chunk(chunk, paper['title'])
                chunk_summaries.append(chunk_summary)
            return self._combine_chunk_summaries(chunk_summaries, paper['title'])
    
    def _summarize_chunk(self, text, title):
        """Summarize a single chunk of text"""
        prompt = f"""Summarize the following research paper content. Focus on:
- Main contributions
- Methods and approaches used
- Key findings and results
- Limitations mentioned

Paper Title: {title}

Content:
{text}

Provide a concise but comprehensive summary:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert research paper summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def _combine_chunk_summaries(self, summaries, title):
        """Combine multiple chunk summaries into coherent summary"""
        combined_text = "\n\n".join([f"Part {i+1}: {s}" for i, s in enumerate(summaries)])
        
        prompt = f"""The following are summaries of different parts of the same research paper.
Combine them into a single, coherent summary that captures all key points:

Paper Title: {title}

{combined_text}

Provide a unified summary:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at synthesizing information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        return response.choices[0].message.content.strip()


def create_summarizer_agent(model="gpt-3.5-turbo"):
    """Factory function to create summarizer agent"""
    return SummarizerAgent(model=model)
