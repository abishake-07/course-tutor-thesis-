from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TransactionTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, gt=0, description="Duration in minutes")
    tags: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, gt=0)
    actual_duration: Optional[int] = Field(None, gt=0)
    tags: Optional[str] = None

class Task(TaskBase):
    id: int
    actual_duration: Optional[int]
    ai_suggestions: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    owner_id: int

    class Config:
        from_attributes = True

# Budget Category schemas
class BudgetCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    monthly_limit: Optional[float] = Field(None, gt=0)
    color: str = Field("#3498db", pattern=r"^#[0-9a-fA-F]{6}$")

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategory(BudgetCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Budget Item schemas
class BudgetItemBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    transaction_type: TransactionTypeEnum
    transaction_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None

class BudgetItemCreate(BudgetItemBase):
    pass

class BudgetItemUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionTypeEnum] = None
    transaction_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None

class BudgetItem(BudgetItemBase):
    id: int
    ai_category_suggestion: Optional[str]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    category: Optional[BudgetCategory]

    class Config:
        from_attributes = True

# AI Interaction schemas
class AIInteractionCreate(BaseModel):
    interaction_type: str
    user_input: Optional[str] = None
    context_data: Optional[str] = None

class AIInteraction(BaseModel):
    id: int
    user_id: int
    interaction_type: str
    user_input: Optional[str]
    ai_response: Optional[str]
    context_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Response schemas
class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    overdue_tasks: int

class BudgetSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    monthly_income: float
    monthly_expenses: float
    categories_summary: List[dict]

class DashboardResponse(BaseModel):
    task_stats: TaskStats
    budget_summary: BudgetSummary
    recent_tasks: List[Task]
    recent_transactions: List[BudgetItem]

# Voice command schemas
class VoiceCommand(BaseModel):
    command: str
    audio_data: Optional[str] = None  # Base64 encoded audio

class VoiceResponse(BaseModel):
    success: bool
    message: str
    action_performed: Optional[str] = None
    data: Optional[dict] = None