from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import APIResponse

class DomainResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True

class RoadmapTopic(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    order_index: int
    icon: Optional[str] = None
    unlock_percentage: float
    learning_objectives: List[str]
    total_questions: int
    solved_count: int
    is_unlocked: bool
    prerequisites: List[str]

class DomainHeader(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class DomainRoadmapData(BaseModel):
    domain: DomainHeader
    topics: List[RoadmapTopic]

class DomainListResponse(APIResponse[List[DomainResponse]]):
    pass

class RoadmapResponse(APIResponse[DomainRoadmapData]):
    pass
