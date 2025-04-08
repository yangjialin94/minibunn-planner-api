from datetime import date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user_id
from app.models.task import Task
from app.schemas.task import CompletionOut, TaskCreate, TaskOut, TaskUpdate

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

    # Add default title if not provided
    if not task.title:
        task.title = "New Task"

    # Create the task(s)
    created_tasks = []
    for i in range(repeatable_days):
        task_date = task.date + timedelta(days=i)

        # Shift existing tasks' order by 1
        db.query(Task).filter(Task.user_id == user_id, Task.date == task_date).update(
            {Task.order: Task.order + 1}
        )

        new_task = Task(
            user_id=user_id,
            date=task_date,
            title=task.title,
            note=task.note,
            is_completed=task.is_completed,
            order=1,
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

    # Enforce only one type of update at a time
    update_fields = set(update_data.keys())
    groups = {
        "order": {"order"},
        "text": {"title", "note"},
        "completed": {"is_completed"},
    }

    matched_groups = [group for group, keys in groups.items() if update_fields & keys]
    if len(matched_groups) > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one type of update is allowed per request (order, title/note, or is_completed).",
        )

    # Handle order update
    if "order" in update_fields:
        new_order = update_data.get("order")
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

    # Handle title/note update
    elif {"title", "note"} & update_fields:
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
                setattr(task, key, value)

    # Handle is_completed update
    elif "is_completed" in update_fields:
        new_status = update_data["is_completed"]
        task.is_completed = new_status

        # Get all tasks for the same day (excluding the current task)
        same_day_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == task.date, Task.id != task.id)
            .order_by(Task.order)
            .all()
        )

        if new_status:
            # If marking as completed, move the task to the last position.
            for t in same_day_tasks:
                if t.order > task.order:
                    t.order -= 1
            task.order = len(same_day_tasks) + 1
        else:
            # If marking as incomplete, move the task to the first position.
            for t in same_day_tasks:
                t.order += 1
            task.order = 1

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


@router.get("/completion/", response_model=List[CompletionOut])
def get_completion_status(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    # Create an expression to sum up completed tasks (1 if completed, else 0)
    completed_sum = func.sum(case((Task.is_completed == True, 1), else_=0)).label(
        "completed"
    )

    # Query for each day: count total tasks and sum the completed tasks.
    results = (
        db.query(
            Task.date,
            func.count(Task.id).label("total"),
            completed_sum,
        )
        .filter(
            Task.user_id == user_id,
            Task.date.between(start, end),
        )
        .group_by(Task.date)
        .order_by(Task.date)
        .all()
    )

    # Format the results
    completions = [
        {
            "date": row.date,
            "total": row.total,
            "completed": row.completed or 0,
        }
        for row in results
    ]
    return completions
