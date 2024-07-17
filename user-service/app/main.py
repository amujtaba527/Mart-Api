from typing import Annotated
from fastapi import FastAPI,Depends,HTTPException
from requests import Session
from app.models.user_model import User,UserCreate
from sqlmodel import Session, SQLModel
from contextlib import asynccontextmanager
from app.db_engine import engine
from app.crud.user_crud import get_user_by_email,create_user
from bcrypt import hashpw, checkpw
from jose import  jwt

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
 

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    return {"Hello": "User Service"}


@app.post("/register/")
def user_create(user: UserCreate, session: Session = Depends(get_session)):
    try:
        return create_user(user=user, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
@app.get("/login", response_model=User)
def get_user(user_email: str, password: str, session: Annotated[Session, Depends(get_session)]):
    isUser = get_user_by_email(user_email=user_email, session=session)

    if not checkpw(password.encode("utf-8"), isUser.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Create JWT token
    user_data = {
        "id": isUser.id,
        "name": isUser.name,
        "email": isUser.email,
        "role": isUser.role
    }
    token = jwt.encode(user_data, "secret", algorithm="HS256")
    return {
        "token": token
    }