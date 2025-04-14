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


def test_update_repeatable_title_and_split_chain(client):
    """
    Tests updating a repeatable task's title on the first task in the chain.
    The current task and all future tasks keep their original repeatable_id.
    The repeatable_days remains unchanged.
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
    assert res.status_code == 200
    task = res.json()
    original_repeatable_id = task["repeatable_id"]
    task_id = task["id"]

    # Update the title of the first task.
    patch = client.patch(f"/tasks/{task_id}", json={"title": "Updated"})
    assert patch.status_code == 200
    updated_task = patch.json()
    assert updated_task["title"] == "Updated"

    # The updated task (and consequently the entire chain) will keep the original repeatable_id.
    new_repeatable_id = updated_task["repeatable_id"]
    assert new_repeatable_id == original_repeatable_id

    # repeatable_days remains unchanged (should still be 3)
    assert updated_task["repeatable_days"] == 3

    # Query the chain again.
    end = (date.today() + timedelta(days=2)).isoformat()
    query = client.get(f"/tasks/?start={today}&end={end}")
    chain_tasks = [t for t in query.json() if t["title"] in ["Updated", "Old"]]
    assert len(chain_tasks) == 3

    # All tasks in the chain should have the same original repeatable_id and repeatable_days = 3.
    for t in chain_tasks:
        assert t["repeatable_id"] == original_repeatable_id
        assert t["repeatable_days"] == 3


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


def test_update_repeatable_second_item_and_split_chain(client):
    """
    Tests updating the second task in a repeatable chain.
    """
    # Create a chain of 5 repeatable tasks.
    today = date.today()
    today_str = today.isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today_str,
            "title": "Chain Task",
            "note": "Repeat this",
            "repeatable_days": 5,
        },
    )
    assert res.status_code == 200
    first_task = res.json()
    original_repeatable_id = first_task["repeatable_id"]
    assert original_repeatable_id is not None

    # Query tasks to ensure all 5 were created.
    end_date_str = (today + timedelta(days=4)).isoformat()
    res_chain = client.get(f"/tasks/?start={today_str}&end={end_date_str}")
    chain_tasks = [t for t in res_chain.json() if t["title"] == "Chain Task"]
    assert len(chain_tasks) == 5

    # Identify the second task (by date ordering).
    sorted_chain = sorted(chain_tasks, key=lambda t: t["date"])
    second_task = sorted_chain[1]
    second_task_id = second_task["id"]

    # Update the title of the second task.
    patch_res = client.patch(
        f"/tasks/{second_task_id}", json={"title": "Updated Chain Task"}
    )
    assert patch_res.status_code == 200
    updated_second = patch_res.json()
    assert updated_second["repeatable_id"] == original_repeatable_id
    assert updated_second["repeatable_days"] == 4

    # Query the chain again.
    res_chain = client.get(f"/tasks/?start={today_str}&end={end_date_str}")
    chain_tasks = sorted(
        [t for t in res_chain.json() if "Chain Task" in t["title"]],
        key=lambda t: t["date"],
    )
    assert len(chain_tasks) == 5

    # The first task (earliest date) should no longer be repeatable.
    first_updated = chain_tasks[0]
    assert first_updated["repeatable_id"] is None
    assert first_updated["repeatable_days"] is None

    # The rest of the tasks (positions 2-5) should have the new repeatable id and repeatable_days = 4.
    for t in chain_tasks[1:]:
        assert t["repeatable_id"] == original_repeatable_id
        assert t["repeatable_days"] == 4

    # Also check that the update was applied: the title of the updated second task should be updated.
    updated_titles = [t["title"] for t in chain_tasks]
    assert "Updated Chain Task" in updated_titles


def test_delete_repeatable_middle_task_splits_chain(client):
    """
    Tests that deleting a middle repeatable task splits the chain.
    All tasks with a date >= that of the deleted task are removed.
    The only previous task (the first one) is removed from the chain.
    """
    # Create a chain of 4 repeatable tasks.
    today = date.today()
    today_str = today.isoformat()
    res = client.post(
        "/tasks/",
        json={
            "date": today_str,
            "title": "Chain Task",
            "note": "Repeat this",
            "repeatable_days": 4,
        },
    )
    assert res.status_code == 200
    first_task = res.json()
    original_repeatable_id = first_task["repeatable_id"]
    assert original_repeatable_id is not None

    # Query tasks to ensure all 4 were created.
    end_date_str = (today + timedelta(days=3)).isoformat()
    res_chain = client.get(f"/tasks/?start={today_str}&end={end_date_str}")
    chain_tasks = [t for t in res_chain.json() if t["title"] == "Chain Task"]
    assert len(chain_tasks) == 4

    # Identify the second task by sorting the chain by date.
    sorted_chain = sorted(chain_tasks, key=lambda t: t["date"])
    second_task = sorted_chain[1]
    second_task_id = second_task["id"]

    # Delete the second task.
    delete_res = client.delete(f"/tasks/{second_task_id}")
    assert delete_res.status_code == 200

    # Query tasks again for the same date range.
    res_chain_after = client.get(f"/tasks/?start={today_str}&end={end_date_str}")
    remaining_tasks = [t for t in res_chain_after.json() if t["title"] == "Chain Task"]

    # Expect that tasks with date >= second task's date are deleted,
    # so only one task (the first task) remains.
    assert len(remaining_tasks) == 1

    # The remaining task (first in the chain) should no longer be repeatable.
    remaining = remaining_tasks[0]
    assert remaining["repeatable_id"] is None
    assert remaining["repeatable_days"] is None
