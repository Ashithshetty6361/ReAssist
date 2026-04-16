from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class RelevanceGrade(BaseModel):
    binary_score: Literal["yes", "no"]

class PaperSchema(BaseModel):
    title: str
    authors: List[str] = []
    abstract: str = ""
    year: Union[int, str] = "Unknown"
    pdf_url: str = ""
    source: str = ""
    arxiv_id: Optional[str] = None
    semantic_id: Optional[str] = None

class SearchResult(BaseModel):
    papers: List[PaperSchema]
    count: int
    success: bool
    error: Optional[str] = None

class VerificationResult(BaseModel):
    faithful: bool
    confidence: float = Field(ge=0, le=1)
    unsupported_claims: List[str] = []
    summary: str

class SynthesisResult(BaseModel):
    synthesis: str
    paper_count: int
    papers_analyzed: List[str]
    success: bool
    error: Optional[str] = None

class GapResult(BaseModel):
    gaps: str
    success: bool
    error: Optional[str] = None

class IdeaResult(BaseModel):
    ideas: List[dict]
    idea_count: int
    success: bool
    error: Optional[str] = None
