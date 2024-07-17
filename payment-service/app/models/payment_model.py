from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Payment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_id: int
    user_id: int
    amount: float
    currency: str
    status: str
    created_at: datetime = Field(default_factory=datetime.now(timezone.now))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.now))