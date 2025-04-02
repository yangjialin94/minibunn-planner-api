from datetime import date

import pytest


def test_get_or_create_journal(client):
    """
    Tests getting or creating a journal for today's date.
    """
    # Get journal for today's date
    today = date.today().isoformat()
    res = client.get(f"/journals/?date={today}")

    # Check response
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == today
    assert data["subject"] == ""
    assert data["entry"] == ""


def test_post_new_journal_success(client):
    """
    Tests creating a new journal entry.
    """
    # Create a new journal
    new_date = date.today().replace(day=1).isoformat()
    res = client.post(
        "/journals/",
        json={
            "date": new_date,
            "subject": "First Journal",
            "entry": "Testing journal POST",
        },
    )

    # Check response
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == new_date
    assert data["subject"] == "First Journal"
    assert data["entry"] == "Testing journal POST"


def test_post_journal_already_exists(client):
    """
    Tests creating a journal entry when one already exists for the date.
    """
    # Create a new journal
    today = date.today().isoformat()
    client.post(
        "/journals/",
        json={
            "date": today,
            "subject": "Should Only Exist Once",
            "entry": "Testing duplicate",
        },
    )

    # Try to create another journal for the same date
    res = client.post(
        "/journals/",
        json={
            "date": today,
            "subject": "Duplicate",
            "entry": "This should fail",
        },
    )

    # Check response
    assert res.status_code == 400
    assert res.json()["detail"] == "Journal already exists for this date"


def test_patch_update_journal(client):
    """
    Tests updating a journal entry.
    """
    # Get journal for today's date
    today = date.today().isoformat()
    journal = client.get(f"/journals/?date={today}").json()

    # Update journal entry
    journal_id = journal["id"]
    res = client.patch(
        f"/journals/{journal_id}",
        json={
            "subject": "Updated Subject",
            "entry": "Updated entry text.",
        },
    )

    # Check response
    assert res.status_code == 200
    updated = res.json()
    assert updated["subject"] == "Updated Subject"
    assert updated["entry"] == "Updated entry text."


def test_patch_nonexistent_journal(client):
    """
    Tests updating a journal that doesn't exist.
    """
    # Try to update a journal that doesn't exist
    res = client.patch("/journals/9999", json={"subject": "Ghost update"})

    # Check response
    assert res.status_code == 404
    assert res.json()["detail"] == "Journal not found"
