"""
Helper utilities for Research Intelligence Engine
Text processing, chunking, and data handling functions
"""

import re
import tiktoken


def count_tokens(text, model="gpt-3.5-turbo"):
    """
    Count tokens in text using tiktoken
    
    Args:
        text: Input text
        model: Model name for tokenizer
    
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


def chunk_text(text, max_tokens=2000, model="gpt-3.5-turbo"):
    """
    Split text into chunks based on token count
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk
        model: Model name for tokenizer
    
    Returns:
        List of text chunks
    """
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para, model)
        
        # If single paragraph exceeds max tokens, split by sentences
        if para_tokens > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence, model)
                if current_tokens + sentence_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                    current_tokens = sentence_tokens
                else:
                    current_chunk += " " + sentence
                    current_tokens += sentence_tokens
        else:
            if current_tokens + para_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
                current_tokens = para_tokens
            else:
                current_chunk += "\n\n" + para
                current_tokens += para_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def clean_text(text):
    """
    Clean and normalize text
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


def truncate_text(text, max_length=500):
    """
    Truncate text to maximum length with ellipsis
    
    Args:
        text: Input text
        max_length: Maximum character length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_paper_metadata(paper):
    """
    Format paper metadata for display
    
    Args:
        paper: Paper dictionary with metadata
    
    Returns:
        Formatted string
    """
    title = paper.get('title', 'Unknown')
    authors = paper.get('authors', [])
    year = paper.get('year', 'Unknown')
    
    author_str = ", ".join(authors[:3])
    if len(authors) > 3:
        author_str += " et al."
    
    return f"{title} ({year}) - {author_str}"


def extract_keywords(text, max_keywords=10):
    """
    Extract potential keywords from text (simple frequency-based)
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
    
    Returns:
        List of keywords
    """
    # Simple word frequency approach
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    
    # Common stop words
    stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 
                  'their', 'which', 'were', 'they', 'these', 'than',
                  'some', 'such', 'into', 'also', 'other', 'more'}
    
    words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:max_keywords]]


def combine_summaries(summaries, separator="\n\n---\n\n"):
    """
    Combine multiple summaries into one document
    
    Args:
        summaries: List of summary strings
        separator: Separator between summaries
    
    Returns:
        Combined summary string
    """
    return separator.join(summaries)


def validate_paper_data(paper):
    """
    Validate that paper data has required fields
    
    Args:
        paper: Paper dictionary
    
    Returns:
        Boolean indicating validity
    """
    required_fields = ['title', 'authors', 'abstract']
    return all(field in paper and paper[field] for field in required_fields)
