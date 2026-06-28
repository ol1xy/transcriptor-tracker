from pydantic import BaseModel
from typing import List, Optional


class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = None
    is_smart: bool


class SummaryModel(BaseModel):
    context: str
    decisions: List[str]
    open_questions: List[str]
    conflicts: List[str]
    next_actions: List[ActionItem]
