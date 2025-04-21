from datetime import date, timedelta

import pytest


def test_create_single_task(client):
    """
    Tests creating a single one-time task.
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


def test_create_task_inserts_at_beginning(client):
    """
    Tests that creating a new task for a given date inserts it at order 1.
    Existing tasks for the same date are shifted down (their order is incremented).
    """
    # Create a task for today
    today = date.today().isoformat()
    res1 = client.post(
        "/tasks/",
        json={"date": today, "title": "First Task", "note": ""},
    )

    # Verify the order of the first task
    assert res1.status_code == 200
    first_task = res1.json()
    assert first_task["order"] == 1

    # Create a second task for the same date
    res2 = client.post(
        "/tasks/",
        json={"date": today, "title": "Second Task", "note": ""},
    )

    # Verify the order of the second task
    assert res2.status_code == 200
    second_task = res2.json()
    assert second_task["order"] == 1

    # Check that the first task's order has been incremented
    res = client.get(f"/tasks/?start={today}&end={today}")
    tasks = sorted(res.json(), key=lambda t: t["order"])
    ordered_titles = [t["title"] for t in tasks]
    expected_order = ["Second Task", "First Task"]
    assert (
        ordered_titles == expected_order
    ), f"Expected order {expected_order}, got {ordered_titles}"


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

    # Reorder "Task 1" to be first
    res = client.get(f"/tasks/?start={today}&end={today}")
    tasks = res.json()
    task1_id = next(t["id"] for t in tasks if t["title"] == "Task 1")
    patch = client.patch(f"/tasks/{task1_id}", json={"order": 1})
    assert patch.status_code == 200

    # Check the order after reordering
    updated = client.get(f"/tasks/?start={today}&end={today}").json()
    ordered_titles = [t["title"] for t in sorted(updated, key=lambda x: x["order"])]
    expected_order = ["Task 1", "Task 3", "Task 2"]
    assert (
        ordered_titles == expected_order
    ), f"Expected order {expected_order}, got {ordered_titles}"


def test_update_is_completed_to_incomplete_moves_before_completed(client):
    """
    Tests that when a task is updated from completed (True) to incomplete (False),
    it is moved to just before the first completed task on the same day.
    """
    # Create 4 tasks on the same day.
    today = date.today().isoformat()
    titles = ["Task A", "Task B", "Task C", "Task D"]
    for title in titles:
        client.post(
            "/tasks/",
            json={"date": today, "title": title, "note": ""},
        )

    # Retrieve tasks and check initial order.
    res = client.get(f"/tasks/?start={today}&end={today}")
    tasks = res.json()
    task_ids = {t["title"]: t["id"] for t in tasks}

    # Mark Task C as complete.
    patch_c = client.patch(f"/tasks/{task_ids['Task C']}", json={"is_completed": True})
    assert patch_c.status_code == 200

    # Mark Task D as complete.
    patch_d = client.patch(f"/tasks/{task_ids['Task D']}", json={"is_completed": True})
    assert patch_d.status_code == 200

    # After marking complete, expected order becomes:
    # Order 1: Task B, Order 2: Task A, Order 3: Task C, Order 4: Task D.
    res = client.get(f"/tasks/?start={today}&end={today}")
    tasks = sorted(res.json(), key=lambda t: t["order"])
    orders = {t["title"]: t["order"] for t in tasks}
    assert orders["Task B"] == 1
    assert orders["Task A"] == 2
    assert orders["Task C"] == 3
    assert orders["Task D"] == 4

    # Now update Task D to be incomplete.
    patch_d_incomplete = client.patch(
        f"/tasks/{task_ids['Task D']}", json={"is_completed": False}
    )
    assert patch_d_incomplete.status_code == 200
    updated_d = patch_d_incomplete.json()
    assert updated_d["is_completed"] is False

    # Retrieve tasks and verify new ordering.
    res = client.get(f"/tasks/?start={today}&end={today}")
    tasks = sorted(res.json(), key=lambda t: t["order"])
    ordered_titles = [t["title"] for t in tasks]

    # Since Task D becomes incomplete, it moves to the top.
    expected_order = ["Task D", "Task B", "Task A", "Task C"]
    assert (
        ordered_titles == expected_order
    ), f"Expected order {expected_order}, got {ordered_titles}"


def test_completion_status_route(client):
    """
    Tests that the completion status route returns the correct summary.
    """
    # Define dates
    day1 = date.today()
    day2 = day1 + timedelta(days=1)
    day1_str = day1.isoformat()
    day2_str = day2.isoformat()

    # Create tasks for Day 1.
    res = client.post(
        "/tasks/",
        json={"date": day1_str, "title": "Task 1", "note": "", "is_completed": True},
    )
    assert res.status_code == 200

    res = client.post(
        "/tasks/",
        json={"date": day1_str, "title": "Task 2", "note": "", "is_completed": True},
    )
    assert res.status_code == 200

    res = client.post(
        "/tasks/",
        json={"date": day1_str, "title": "Task 3", "note": "", "is_completed": False},
    )
    assert res.status_code == 200

    # Create tasks for Day 2.
    res = client.post(
        "/tasks/",
        json={"date": day2_str, "title": "Task 4", "note": "", "is_completed": True},
    )
    assert res.status_code == 200

    res = client.post(
        "/tasks/",
        json={"date": day2_str, "title": "Task 5", "note": "", "is_completed": False},
    )
    assert res.status_code == 200

    # Query the /completion/ endpoint for the range covering both days.
    res = client.get(f"/tasks/completion/?start={day1_str}&end={day2_str}")
    assert res.status_code == 200
    data = res.json()

    # Expected summaries for each day.
    expected = [
        {"date": day1_str, "total": 3, "completed": 2},
        {"date": day2_str, "total": 2, "completed": 1},
    ]

    assert len(data) == len(
        expected
    ), f"Expected {len(expected)} days but got {len(data)}."

    # Check each day's summary.
    for result, exp in zip(data, expected):
        assert result["date"] == exp["date"]
        assert result["total"] == exp["total"]
        assert result["completed"] == exp["completed"]


def test_update_task_date_and_reorder(client):
    """
    Tests updating a task's date.
    The task should move to the new date and be inserted at order 1,
    pushing existing tasks on the new date down by 1.
    """
    today = date.today()
    today_str = today.isoformat()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    # Create two tasks on today
    res1 = client.post(
        "/tasks/", json={"date": today_str, "title": "Task A", "note": ""}
    )
    res2 = client.post(
        "/tasks/", json={"date": today_str, "title": "Task B", "note": ""}
    )
    assert res1.status_code == 200 and res2.status_code == 200
    task_b_id = res2.json()["id"]

    # Create one task on tomorrow
    res3 = client.post(
        "/tasks/", json={"date": tomorrow_str, "title": "Task C", "note": ""}
    )
    assert res3.status_code == 200

    # Patch task B's date to tomorrow
    patch = client.patch(f"/tasks/{task_b_id}", json={"date": tomorrow_str})
    print("PATCH error details:", patch.json())
    assert patch.status_code == 200
    moved = patch.json()
    assert moved["date"] == tomorrow_str
    assert moved["order"] == 1

    # Fetch tasks on today and tomorrow
    today_tasks = client.get(f"/tasks/?start={today_str}&end={today_str}").json()
    tomorrow_tasks = client.get(
        f"/tasks/?start={tomorrow_str}&end={tomorrow_str}"
    ).json()

    # Verify today's tasks are reordered correctly
    assert len(today_tasks) == 1
    assert today_tasks[0]["title"] == "Task A"
    assert today_tasks[0]["order"] == 1

    # Verify tomorrow's tasks are in correct order
    ordered_tomorrow = sorted(tomorrow_tasks, key=lambda t: t["order"])
    expected_titles = ["Task B", "Task C"]
    actual_titles = [t["title"] for t in ordered_tomorrow]
    assert (
        actual_titles == expected_titles
    ), f"Expected {expected_titles}, got {actual_titles}"


def test_get_tasks_within_date_range(client):
    """
    Tests that querying tasks within a specific date range
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Create tasks on three different days
    client.post(
        "/tasks/", json={"date": yesterday.isoformat(), "title": "Y", "note": ""}
    )
    client.post("/tasks/", json={"date": today.isoformat(), "title": "T", "note": ""})
    client.post(
        "/tasks/", json={"date": tomorrow.isoformat(), "title": "Tm", "note": ""}
    )

    # Query for today only
    res = client.get(f"/tasks/?start={today.isoformat()}&end={today.isoformat()}")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "T"


def test_delete_task_reorders_remaining(client):
    """
    Tests that deleting a task reorders the remaining tasks correctly.
    """
    today = date.today().isoformat()

    # Create 3 tasks
    ids = []
    for title in ["A", "B", "C"]:
        res = client.post("/tasks/", json={"date": today, "title": title, "note": ""})
        ids.append(res.json()["id"])

    # Delete task B (originally order 2)
    res = client.delete(f"/tasks/{ids[1]}")
    assert res.status_code == 200

    # Verify new order is [C, A]
    res = client.get(f"/tasks/?start={today}&end={today}")
    ordered = sorted(res.json(), key=lambda t: t["order"])
    assert [t["title"] for t in ordered] == ["C", "A"]
    assert [t["order"] for t in ordered] == [1, 2]


def test_patch_task_title_and_note_only(client):
    """
    Tests that updating only the title and note of a task works correctly.
    """
    today = date.today().isoformat()
    res = client.post(
        "/tasks/", json={"date": today, "title": "Old", "note": "Old note"}
    )
    task_id = res.json()["id"]

    patch = client.patch(f"/tasks/{task_id}", json={"title": "New", "note": "New note"})
    assert patch.status_code == 200
    data = patch.json()
    assert data["title"] == "New"
    assert data["note"] == "New note"


def test_patch_invalid_order(client):
    """
    Tests that trying to set an invalid order on a task
    """
    today = date.today().isoformat()
    res = client.post("/tasks/", json={"date": today, "title": "Only", "note": ""})
    task_id = res.json()["id"]

    patch = client.patch(f"/tasks/{task_id}", json={"order": 5})
    assert patch.status_code == 200
    assert patch.json()["order"] == 1
