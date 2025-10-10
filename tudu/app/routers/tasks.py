from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate, Task as TaskSchema, TaskStats
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TaskSchema)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    db_task = Task(
        **task.dict(),
        owner_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's tasks with optional filtering"""
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task statistics for the current user"""
    base_query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    total_tasks = base_query.count()
    completed_tasks = base_query.filter(Task.status == "completed").count()
    pending_tasks = base_query.filter(Task.status == "pending").count()
    in_progress_tasks = base_query.filter(Task.status == "in_progress").count()
    
    # Count overdue tasks
    now = datetime.utcnow()
    overdue_tasks = base_query.filter(
        Task.due_date < now,
        Task.status.in_(["pending", "in_progress"])
    ).count()
    
    return TaskStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        overdue_tasks=overdue_tasks
    )

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # Set completion time if status is changed to completed
    if update_data.get("status") == "completed" and db_task.status != "completed":
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.get("/upcoming/week", response_model=List[TaskSchema])
async def get_upcoming_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks due in the next 7 days"""
    now = datetime.utcnow()
    week_later = now + timedelta(days=7)
    
    tasks = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.due_date.between(now, week_later),
        Task.status.in_(["pending", "in_progress"])
    ).order_by(Task.due_date).all()
    
    return tasks

@router.post("/{task_id}/complete", response_model=TaskSchema)
async def complete_task(
    task_id: int,
    actual_duration: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = "completed"
    db_task.completed_at = datetime.utcnow()
    if actual_duration:
        db_task.actual_duration = actual_duration
    
    db.commit()
    db.refresh(db_task)
    return db_task