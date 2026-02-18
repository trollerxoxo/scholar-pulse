from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import StrEnum

class Status(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

class Task(SQLModel):
    id: Optional[int] = Field(default=None)
    description: str
    status: Status = Field(default=Status.TODO)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

