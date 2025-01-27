from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
import uuid
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr = Field(unique=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)



class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdateMe(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model representation (if needed)
class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    items: List['TaskModel'] = []


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: UUID


class UsersPublic(BaseModel):
    data: List[UserPublic]
    count: int

from enum import Enum

class TaskOutcome(str, Enum):
   PASS = "pass"
   FAIL = "fail"
   PENDING = "pending"


class TaskModel(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    id: uuid.UUID
    status: TaskOutcome
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    status: TaskOutcome




# Generic message
class TaskResponse(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    id: uuid.UUID
    status: TaskOutcome
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class PaginatedTaskResponse(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of tasks per page")
    tasks: List[TaskResponse] = Field(..., description="List of tasks for current page")



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Optional[str] = None


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# the below model has been done optionally to implement task priority

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskPriority(TaskModel):
  
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    class Config:
        from_attributes = True