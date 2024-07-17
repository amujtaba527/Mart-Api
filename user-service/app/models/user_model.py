from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id:int = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: str

class UserCreate(SQLModel, table=False):
    name: str
    email: str
    password: str
    role: str