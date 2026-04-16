"""
PDF Parser Utility - Extracts text from research papers
Single Responsibility: PDF text extraction ONLY
"""

import os
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        PDF_LIBRARY = None


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary with:
            - text: Extracted text
            - title: Extracted title (if available)
            - page_count: Number of pages
            - success: Boolean
            - error: Error message if failed
    """
    if not os.path.exists(pdf_path):
        return {
            'text': None,
            'title': None,
            'page_count': 0,
            'success': False,
            'error': f'File not found: {pdf_path}'
        }
    
    if PDF_LIBRARY is None:
        return {
            'text': None,
            'title': None,
            'page_count': 0,
            'success': False,
            'error': 'No PDF library installed. Install: pip install pdfplumber'
        }
    
    try:
        if PDF_LIBRARY == 'pdfplumber':
            return _extract_with_pdfplumber(pdf_path)
        else:
            return _extract_with_pypdf2(pdf_path)
    except Exception as e:
        return {
            'text': None,
            'title': None,
            'page_count': 0,
            'success': False,
            'error': f'PDF extraction failed: {str(e)}'
        }


def _extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber (preferred)"""
    with pdfplumber.open(pdf_path) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        
        full_text = '\n\n'.join(pages)
        
        # Try to extract title from first page
        title = _extract_title_from_text(full_text)
        
        return {
            'text': full_text,
            'title': title,
            'page_count': len(pdf.pages),
            'success': True,
            'error': None
        }


def _extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2 (fallback)"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pages = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        
        full_text = '\n\n'.join(pages)
        title = _extract_title_from_text(full_text)
        
        return {
            'text': full_text,
            'title': title,
            'page_count': len(reader.pages),
            'success': True,
            'error': None
        }


def _extract_title_from_text(text):
    """
    Heuristic: Extract title from first few lines
    Assumes title is in first 500 chars and is a complete line
    """
    if not text:
        return 'Untitled Paper'
    
    # Get first 500 characters
    header = text[:500]
    
    # Split into lines and get first non-empty, non-abstract line
    lines = [line.strip() for line in header.split('\n') if line.strip()]
    
    for line in lines:
        # Skip common header elements
        if any(skip in line.lower() for skip in ['abstract', 'arxiv:', 'doi:', 'http://', 'www.']):
            continue
        
        # Title is usually the first substantial line
        if len(line) > 10 and len(line) < 200:
            return line
    
    return 'Untitled Paper'


def create_paper_dict_from_pdf(pdf_path, extract_result):
    """
    Convert PDF extraction result to paper dict format
    Compatible with existing agent pipeline
    
    Args:
        pdf_path: Original PDF path
        extract_result: Result from extract_text_from_pdf()
    
    Returns:
        Paper dict in standard format
    """
    return {
        'title': extract_result.get('title', 'Uploaded Paper'),
        'authors': ['Unknown'],  # PDF metadata extraction could be added
        'year': 'Unknown',
        'abstract': extract_result.get('text', '')[:1000] + '...',  # First 1000 chars as "abstract"
        'full_text': extract_result.get('text', ''),
        'source': 'uploaded_pdf',
        'pdf_path': pdf_path,
        'page_count': extract_result.get('page_count', 0)
    }
