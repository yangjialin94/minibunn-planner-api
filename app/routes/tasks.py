from datetime import date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user_id
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

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
    If repeatable_days is provided, create multiple tasks with the same repeatable_id.
    """
    # Generate repeatable_id if task is repeatable
    repeatable_days = task.repeatable_days or 1
    repeatable_id = str(uuid4()) if repeatable_days > 1 else None

    # Create the task(s)
    created_tasks = []
    for i in range(repeatable_days):
        task_date = task.date + timedelta(days=i)

        # Get the current max order for this user and date
        max_order = (
            db.query(func.max(Task.order))
            .filter(Task.user_id == user_id, Task.date == task_date)
            .scalar()
        )
        new_order = (max_order or 0) + 1

        new_task = Task(
            user_id=user_id,
            date=task_date,
            title=task.title,
            note=task.note,
            is_completed=task.is_completed,
            order=new_order,
            repeatable_id=repeatable_id,
            repeatable_days=repeatable_days if repeatable_id else None,
        )

        db.add(new_task)
        created_tasks.append(new_task)

    db.commit()

    # Return the first task created
    db.refresh(created_tasks[0])
    return created_tasks[0]


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Update a task for the current user.
    If the task is repeatable, update all tasks with the same repeatable_id.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)
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

    update_title_or_note = any(k in update_data for k in ["title", "note"])

    # Check if the task is repeatable
    if task.repeatable_id and update_title_or_note:
        old_repeatable_id = task.repeatable_id
        new_repeatable_id = str(uuid4())

        future_tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.repeatable_id == old_repeatable_id,
                Task.date > task.date,
            )
            .all()
        )

        new_repeatable_days = len(future_tasks) + 1

        # Update the current task
        for key, value in update_data.items():
            if key != "order":
                setattr(task, key, value)
        task.repeatable_id = new_repeatable_id
        task.repeatable_days = new_repeatable_days

        # Update other tasks with the same repeatable_id
        for future_task in future_tasks:
            if "title" in update_data:
                future_task.title = update_data["title"]
            if "note" in update_data:
                future_task.note = update_data["note"]
            future_task.repeatable_id = new_repeatable_id
            future_task.repeatable_days = new_repeatable_days
    else:
        # Update the current task
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
    If the task is repeatable, delete all tasks with the same repeatable_id.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    affected_dates = []

    # Check if the task is repeatable
    if task.repeatable_id:
        tasks_to_delete = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.repeatable_id == task.repeatable_id,
                Task.date >= task.date,
            )
            .all()
        )

        affected_dates = list(set(t.date for t in tasks_to_delete))

        # Delete all tasks with the same repeatable_id
        for t in tasks_to_delete:
            db.delete(t)
    else:
        # Delete the single task
        affected_dates = [task.date]
        db.delete(task)

    db.commit()

    # Reorder the remaining tasks
    for d in affected_dates:
        remaining_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == d)
            .order_by(Task.order)
            .all()
        )

        for i, t in enumerate(remaining_tasks, start=1):
            t.order = i

    db.commit()
    return {"message": "Task(s) deleted and reordered"}
