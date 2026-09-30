from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KnowledgeDocument:
    content: str
    domain: str
    topic: str
    subtopic: Optional[str] = None
    role: Optional[str] = None
    interview_type: Optional[str] = None
    difficulty: Optional[str] = None
    concept: Optional[str] = None
    ideal_answer: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    source_type: Optional[str] = None
    source: Optional[str] = None