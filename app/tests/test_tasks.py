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
    # Create a repeatable task chain for 3 days
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
    old_repeatable_id = task["repeatable_id"]
    task_id = task["id"]

    # Update the title of the first task
    patch = client.patch(f"/tasks/{task_id}", json={"title": "Updated"})
    assert patch.status_code == 200
    updated_task = patch.json()
    assert updated_task["title"] == "Updated"

    # Check that the repeatable_id has changed
    new_repeatable_id = updated_task["repeatable_id"]
    assert new_repeatable_id is not None
    assert new_repeatable_id != old_repeatable_id
    assert updated_task["repeatable_days"] == 3

    # Verify that the first task has the new repeatable_id
    end = (date.today() + timedelta(days=2)).isoformat()
    query = client.get(f"/tasks/?start={today}&end={end}")
    chain_tasks = query.json()
    for t in chain_tasks:
        if t["title"] == "Updated":
            assert t["repeatable_id"] == new_repeatable_id
            assert t["repeatable_days"] == 3

    # Ensure that the past tasks are unchanged
    assert len([t for t in chain_tasks if t["title"] == "Updated"]) == 3


def test_patch_multiple_update_types_fails(client):
    """
    Tests that mixing update groups (e.g., order and text fields)
    in a single patch request results in a 400 error.
    """
    today = date.today().isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today,
            "title": "Mixed Update",
            "note": "Initial note",
            "repeatable_days": 2,
        },
    )
    task = res.json()
    task_id = task["id"]

    # Attempt to update both order and title in one request
    patch = client.patch(f"/tasks/{task_id}", json={"order": 2, "title": "New Title"})
    assert patch.status_code == 400

    # Check the error message
    error_detail = patch.json().get("detail", "")
    assert "Only one type of update" in error_detail


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
