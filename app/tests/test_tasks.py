from datetime import date, timedelta

import pytest


def test_create_single_task(client):
    """
    Tests creating a single one-time task.
    Should not include any repeatable_id.
    """
    # Create a task
    today = date.today().isoformat()  # '2025-04-02'
    res = client.post(
        "/tasks/",
        json={"date": today, "title": "One-time task", "note": "Test note"},
    )

    # Check response
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "One-time task"
    assert data["repeatable_id"] is None


def test_create_repeated_tasks(client):
    """
    Tests creating a repeatable task.
    Should create multiple tasks with the same repeatable_id.
    """
    # Create a repeatable task
    today = date.today().isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today,
            "title": "Repeatable",
            "note": "Repeat this",
            "repeatable_days": 3,
        },
    )

    # Check repeatable id was generated
    assert res.status_code == 200
    first = res.json()
    assert first["repeatable_id"] is not None

    # Check repeatable tasks were created
    end = (date.today() + timedelta(days=2)).isoformat()
    query = client.get(f"/tasks/?start={today}&end={end}")
    repeated = [t for t in query.json() if t["title"] == "Repeatable"]
    assert len(repeated) == 3
    assert len(set(t["repeatable_id"] for t in repeated)) == 1


def test_update_repeatable_title_and_split_chain(client):
    """
    Tests updating a repeatable task's title.
    Should update current + future tasks with new repeatable_id.
    Past tasks should remain unchanged.
    """
    # Create a repeatable task
    today = date.today().isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today,
            "title": "Old",
            "note": "repeat note",
            "repeatable_days": 3,
        },
    )
    task = res.json()
    task_id = task["id"]

    # Update title of the first task
    patch = client.patch(f"/tasks/{task_id}", json={"title": "Updated"})
    assert patch.status_code == 200
    assert patch.json()["title"] == "Updated"

    # Check all tasks have the new title
    end = (date.today() + timedelta(days=2)).isoformat()
    query = client.get(f"/tasks/?start={today}&end={end}")
    titles = [t["title"] for t in query.json()]
    assert titles == ["Updated"] * 3

    # Check all tasks have the same repeatable_id
    ids = [t["repeatable_id"] for t in query.json()]
    assert len(set(ids)) == 1


def test_delete_repeatable_and_reorder_remaining(client):
    """
    Tests deleting a repeatable task.
    Should delete all future tasks with same repeatable_id.
    Also ensures remaining tasks on same dates are reordered.
    """
    # Create a repeatable task
    today = date.today().isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today,
            "title": "Delete Me",
            "note": "",
            "repeatable_days": 3,
        },
    )
    first_id = res.json()["id"]

    # Create an unrelated task on the same day
    client.post(
        "/tasks/",
        json={"date": today, "title": "Survivor", "note": ""},
    )

    # Delete first repeatable task
    delete = client.delete(f"/tasks/{first_id}")
    assert delete.status_code == 200

    # Check only the unrelated task remains
    end = (date.today() + timedelta(days=2)).isoformat()
    res = client.get(f"/tasks/?start={today}&end={end}")
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Survivor"
    assert tasks[0]["order"] == 1


def test_reorder_task_within_day(client):
    """
    Tests reordering a task's order in the same day.
    Should shift orders of other tasks correctly.
    """
    # Create 3 tasks on the same day
    today = date.today().isoformat()
    for i in range(3):
        client.post(
            "/tasks/",
            json={"date": today, "title": f"Task {i+1}", "note": ""},
        )

    # Move Task 1 to position 3
    res = client.get(f"/tasks/?start={today}&end={today}")
    task_id = next(t["id"] for t in res.json() if t["title"] == "Task 1")
    patch = client.patch(f"/tasks/{task_id}", json={"order": 3})
    assert patch.status_code == 200

    # Check final order is [Task 2, Task 3, Task 1]
    updated = client.get(f"/tasks/?start={today}&end={today}").json()
    ordered_titles = [t["title"] for t in sorted(updated, key=lambda x: x["order"])]
    assert ordered_titles == ["Task 2", "Task 3", "Task 1"]
