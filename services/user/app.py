# services/user/app.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
from typing import List

# --- Configuration ---
SECRET_KEY = os.getenv("JWT_SECRET", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- Models ---
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class HistoryItem(BaseModel):
    text: str
    created_at: str = None

class SearchHistory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ViewHistory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- FastAPI app instance ---
app = FastAPI(title="User Service")

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adjust as needed; or ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database setup ---
engine = create_engine("sqlite:///./users.db", echo=False)
SQLModel.metadata.create_all(engine)

# --- Utility functions ---
def get_user(username: str) -> User | None:
    with Session(engine) as session:
        return session.exec(select(User).where(User.username == username)).first()

def create_user(username: str, password: str) -> User:
    hashed = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def authenticate_user(username: str, password: str) -> User | None:
    user = get_user(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# --- Startup event: ensure default “user”/“user” exists ---
@app.on_event("startup")
def create_default_user():
    if not get_user("user"):
        create_user("user", "user")
        print("⚡️ Default user/user account created")

# --- Auth and user routes ---
@app.post("/register", response_model=UserRead)
def register(data: UserCreate):
    if get_user(data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(data.username, data.password)
    return UserRead(id=user.id, username=user.username)

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserRead(id=current_user.id, username=current_user.username)

# --- History recording endpoints ---
@app.post("/me/history/search")
def record_search(item: HistoryItem, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        record = SearchHistory(user_id=current_user.id, text=item.text)
        session.add(record)
        session.commit()
    return {"ok": True}

@app.post("/me/history/view")
def record_view(item: HistoryItem, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        record = ViewHistory(user_id=current_user.id, text=item.text)
        session.add(record)
        session.commit()
    return {"ok": True}

# --- History retrieval endpoints ---
@app.get("/me/history/search", response_model=List[HistoryItem])
def get_search_history(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        rows = session.exec(
            select(SearchHistory)
            .where(SearchHistory.user_id == current_user.id)
            .order_by(SearchHistory.created_at.desc())
        ).all()
    return [
        HistoryItem(text=r.text, created_at=r.created_at.isoformat())
        for r in rows
    ]

@app.get("/me/history/view", response_model=List[HistoryItem])
def get_view_history(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        rows = session.exec(
            select(ViewHistory)
            .where(ViewHistory.user_id == current_user.id)
            .order_by(ViewHistory.created_at.desc())
        ).all()
    return [
        HistoryItem(text=r.text, created_at=r.created_at.isoformat())
        for r in rows
    ]

# … import sẵn HistoryItem, get_user, Session, select, SearchHistory, ViewHistory …

@app.get("/users/{username}/history/search", response_model=List[HistoryItem])
def get_search_history_by_username(username: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    with Session(engine) as session:
        rows = session.exec(
            select(SearchHistory)
            .where(SearchHistory.user_id == user.id)
            .order_by(SearchHistory.created_at.desc())
        ).all()
    return [
        HistoryItem(text=r.text, created_at=r.created_at.isoformat())
        for r in rows
    ]

@app.get("/users/{username}/history/view", response_model=List[HistoryItem])
def get_view_history_by_username(username: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    with Session(engine) as session:
        rows = session.exec(
            select(ViewHistory)
            .where(ViewHistory.user_id == user.id)
            .order_by(ViewHistory.created_at.desc())
        ).all()
    return [
        HistoryItem(text=r.text, created_at=r.created_at.isoformat())
        for r in rows
    ]
