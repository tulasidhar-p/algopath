from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import APIResponse
from app.schemas.domain import DomainResponse

class QuestionResponse(BaseModel):
    id: int
    concept_id: int
    title: str
    difficulty: str
    source: str
    url: str
    estimated_solve_time: int
    is_important: bool
    order_index: int
    status: str = "unsolved"
    bookmark: bool = False
    notes: Optional[str] = None
    tags: List[str] = []
    companies: List[str] = []

    class Config:
        from_attributes = True

class ConceptResponse(BaseModel):
    id: int
    pattern_id: int
    name: str
    slug: str
    theory_markdown: Optional[str] = None
    learning_objectives: List[str] = []
    order_index: int
    questions: List[QuestionResponse] = []
    solved_count: int = 0
    total_count: int = 0

    class Config:
        from_attributes = True

class PatternResponse(BaseModel):
    id: int
    topic_id: int
    name: str
    slug: str
    description: Optional[str] = None
    order_index: int
    concepts: List[ConceptResponse] = []
    solved_count: int = 0
    total_count: int = 0

    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    id: int
    domain_id: int
    name: str
    slug: str
    description: Optional[str] = None
    order_index: int
    icon: Optional[str] = None
    unlock_percentage: float
    learning_objectives: List[str] = []
    total_questions: int
    solved_count: int = 0
    is_unlocked: bool = False
    patterns: List[PatternResponse] = []
    prerequisites: List[str] = []

    class Config:
        from_attributes = True

class TopicProgressDetail(BaseModel):
    topic_slug: str
    solved_count: int
    total_count: int
    is_unlocked: bool
    completion_percentage: float

class SolveRequest(BaseModel):
    status: str  # unsolved, solved, revisit
    notes: Optional[str] = None
    solve_time: Optional[int] = None

class BookmarkRequest(BaseModel):
    bookmark: bool
