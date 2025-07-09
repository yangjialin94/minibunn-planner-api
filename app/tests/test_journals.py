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


def test_patch_journal(client):
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


def test_get_or_create_journal_creates_new_empty_journal(client):
    """Test that a new journal is created when none exists for the date"""
    # Use a unique date to ensure no journal exists
    unique_date = "2025-12-25"  # Future date
    res = client.get(f"/journals/?date={unique_date}")

    assert res.status_code == 200
    data = res.json()
    assert data["date"] == unique_date
    assert data["subject"] == ""  # Should be empty string for new journal
    assert data["entry"] == ""  # Should be empty string for new journal

    # Verify the journal was actually created by querying again
    res2 = client.get(f"/journals/?date={unique_date}")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == data["id"]  # Should be the same journal


def test_patch_journal_with_existing_seeded_client(seeded_client):
    """Test patching a journal with the seeded client to cover missing lines"""
    # Create a journal first
    test_date = "2025-02-14"
    res = seeded_client.post(
        "/journals/",
        json={
            "date": test_date,
            "subject": "Original Subject",
            "entry": "Original Entry",
        },
    )
    assert res.status_code == 200
    journal_id = res.json()["id"]

    # Patch the journal - this should cover the missing lines
    patch_res = seeded_client.patch(
        f"/journals/{journal_id}", json={"subject": "New Subject", "entry": "New Entry"}
    )
    assert patch_res.status_code == 200

    data = patch_res.json()
    assert data["subject"] == "New Subject"
    assert data["entry"] == "New Entry"


def test_clear_journal_function_directly():
    """Test the clear_journal function directly to achieve 100% coverage"""
    from unittest.mock import Mock

    from app.models.journal import Journal
    from app.models.user import User
    from app.routes.journals import clear_journal

    # Create mock objects
    mock_db = Mock()
    mock_user = User(
        id=1,
        firebase_uid="test-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )

    # Mock a journal to be cleared
    mock_journal = Mock()
    mock_journal.subject = "Original Subject"
    mock_journal.entry = "Original Entry"

    # Mock the database query chain
    mock_db.query.return_value.filter.return_value.first.return_value = mock_journal

    # Call the function directly
    result = clear_journal(journal_id=1, db=mock_db, user=mock_user)

    # Verify the journal was cleared
    assert mock_journal.subject == ""
    assert mock_journal.entry == ""

    # Verify database operations were called
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_journal)

    # The function should return the journal
    assert result == mock_journal


def test_clear_journal_function_not_found():
    """Test the clear_journal function when journal is not found"""
    from unittest.mock import Mock

    import pytest
    from fastapi import HTTPException

    from app.models.user import User
    from app.routes.journals import clear_journal

    # Create mock objects
    mock_db = Mock()
    mock_user = User(
        id=1,
        firebase_uid="test-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )

    # Mock database query to return None (journal not found)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Call the function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        clear_journal(journal_id=999, db=mock_db, user=mock_user)

    assert exc_info.value.status_code == 404
    assert "Journal not found" in str(exc_info.value.detail)
