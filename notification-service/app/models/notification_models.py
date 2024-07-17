from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    title: str
    message: str
    recipient: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None