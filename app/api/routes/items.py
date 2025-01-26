import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import TaskModel,TaskCreate,TaskUpdate,TaskResponse,Message

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=TaskResponse)
def read_tasks(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve tasks.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(TaskModel)
        count = session.exec(count_statement).one()
        statement = select(TaskModel).offset(skip).limit(limit)
        tasks = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(TaskModel)
            .where(TaskModel.id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(TaskModel)
            .where(TaskModel.id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        tasks = session.exec(statement).all()

    return TaskModel(data=tasks, count=count)


@router.get("/{id}", response_model=TaskResponse)
def read_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get task by ID.
    """
    task = session.get(TaskModel, id)
    if not task:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (task.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return task


@router.post("/", response_model=TaskResponse)
def create_task(
    *, session: SessionDep, current_user: CurrentUser, task_in: TaskCreate
) -> Any:
    """
    Create new task.
    """
    task = TaskResponse.model_validate(task_in, update={"owner_id": current_user.id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.put("/{id}", response_model=TaskResponse)
def update_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    task_in: TaskUpdate,
) -> Any:
    """
    Update an task.
    """
    task = session.get(TaskModel, id)
    if not task:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (task.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = task_in.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_dict)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{id}")
def delete_task(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an task.
    """
    task = session.get(TaskModel, id)
    if not task:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (task.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(task)
    session.commit()
    return Message(message="Item deleted successfully")