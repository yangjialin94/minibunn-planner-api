from datetime import date
from typing import List, Optional

from core.database import get_db
from deps.auth import get_user_id
from fastapi import APIRouter, Depends, HTTPException
from models.task import Task
from schemas.task import TaskCreate, TaskOut, TaskUpdate
from sqlalchemy.orm import Session

# Create a router
router = APIRouter()


@router.get("/", response_model=List[TaskOut])
def get_tasks(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Get tasks for the current user between the start and end dates.
    """
    query = db.query(Task).filter(Task.user_id == user_id)
    if start and end:
        query = query.filter(Task.date.between(start, end))
    return query.order_by(Task.order).all()


@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Create a new task for the current user.
    """
    # Get the current max order for this user and date
    max_order = (
        db.query(func.max(Task.order))
        .filter(Task.user_id == user_id, Task.date == task.date)
        .scalar()
    )
    new_order = (max_order or 0) + 1

    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Update a task for the current user.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.dict(exclude_unset=True)
    new_order = update_data.get("order")

    # Handle order reordering
    if new_order is not None and new_order != task.order:
        if new_order < 1:
            raise HTTPException(status_code=400, detail="Order must be 1 or greater")

        same_day_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == task.date, Task.id != task_id)
            .order_by(Task.order)
            .all()
        )

        # Ensure the new order is within the valid range
        max_order = len(same_day_tasks) + 1
        if new_order > max_order:
            new_order = max_order

        for t in same_day_tasks:
            # Shift tasks down
            if task.order < new_order:
                if task.order < t.order <= new_order:
                    t.order -= 1
            # Shift tasks up
            else:
                if new_order <= t.order < task.order:
                    t.order += 1

        task.order = new_order

    # Update other task fields
    for key, value in update_data.items():
        # Skip the order field
        if key != "order":
            setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Delete a task for the current user.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
