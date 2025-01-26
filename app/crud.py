import uuid
from typing import Any
from typing import Optional
from sqlmodel import Session, select,func
from fastapi import HTTPException
from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate, TaskModel,TaskCreate,TaskUpdate,TaskResponse,PaginatedTaskResponse, TaskOutcome
from fastapi_pagination import Page
import datetime

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_task(*, session: Session, item_in: TaskCreate, owner_id: uuid.UUID) -> TaskResponse:
    db_item = TaskModel.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_task(*, session: Session, db_task: TaskModel, task_update: TaskUpdate)->TaskResponse:
 
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    session.commit()
    session.refresh(db_task)
    return db_task

def read_task(*, session: Session, task_id: int) -> TaskModel:
    db_task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return db_task

def delete_task(*, session: Session, db_task: TaskModel):
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    session.delete(db_task)
    session.commit()
    return {"detail": "Task successfully deleted"}

def list_tasks(
    *,
    session: Session, 
    status: Optional[TaskOutcome] = None, 
    page: int = 1, 
    page_size: int = 10
) -> PaginatedTaskResponse:
    query = select(TaskModel)

    if status is not None:
        query = query.where(TaskModel.status == status)

    total_tasks = session.scalar(select(func.count()).select_from(query.subquery()))
    
    offset = (page - 1) * page_size
    tasks = session.exec(query.offset(offset).limit(page_size)).all()
    
    return PaginatedTaskResponse(
        total_tasks=total_tasks,
        page=page,
        page_size=page_size,
        tasks=[
            TaskResponse.model_validate(task) for task in tasks
        ]
    )