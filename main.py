import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "default-key")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeSerializer(SECRET_KEY)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    owner_id = Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Cloud Task Manager - 2324802010354")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    token = authorization.split(" ")[1]
    try:
        data = serializer.loads(token)
        user = db.query(User).filter(User.id == data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

class AuthSchema(BaseModel):
    username: str
    password: str

class TaskSchema(BaseModel):
    title: str
    description: str = ""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/register")
def register(payload: AuthSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    user = User(username=payload.username, hashed_password=pwd_context.hash(payload.password))
    db.add(user)
    db.commit()
    return {"message": "Đăng cý thanh công"}

@app.post("/api/login")
def login(payload: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc lật khẩu")
    token = serializer.dumps({"user_id": user.id, "username": user.username})
    return {"token": token, "username": user.username}

@app.get("/api/tasks")
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.owner_id == user.id).all()

@app.post("/api/tasks")
def create_task(payload: TaskSchema, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = Task(title=payload.title, description=payload.description, owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskSchema, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục")
    task.title = payload.title
    task.description = payload.description
    db.commit()
    return task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục")
    db.delete(task)
    db.commit()
    return {"message": " Đã xóa"}
