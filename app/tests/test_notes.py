from datetime import date


def test_create_single_note(client):
    """
    Test creating a new note.
    """
    res = client.post("/notes/", json={"detail": "Test note"})
    assert res.status_code == 200
    data = res.json()
    assert data["detail"] == "Test note"
    assert data["order"] == 1


def test_notes_are_ordered(client):
    """
    Test that notes are ordered by the 'order' field when retrieved.
    """
    # Add 3 notes
    client.post("/notes/", json={"detail": "Note A"})
    client.post("/notes/", json={"detail": "Note B"})
    client.post("/notes/", json={"detail": "Note C"})

    res = client.get("/notes/")
    notes = res.json()
    assert len(notes) == 3
    assert [n["detail"] for n in notes] == ["Note C", "Note B", "Note A"]
    assert [n["order"] for n in notes] == [1, 2, 3]


def test_update_note_detail(client):
    """
    Test updating the detail of a single note.
    """
    post = client.post("/notes/", json={"detail": "Original"})
    note_id = post.json()["id"]

    patch = client.patch(f"/notes/{note_id}", json={"detail": "Updated!"})
    assert patch.status_code == 200
    updated = patch.json()
    assert updated["detail"] == "Updated!"
    assert updated["date"] == date.today().isoformat()


def test_update_note_order(client):
    """
    Test reordering a note shifts other notes correctly.
    """
    # Create 3 notes: newest is Note 3 at order 1
    ids = []
    for i in range(3):
        res = client.post("/notes/", json={"detail": f"Note {i+1}"})
        ids.append(res.json()["id"])

    # At this point: order is [Note 3, Note 2, Note 1]

    # Move Note 1 (currently order 3) to order 1
    patch = client.patch(f"/notes/{ids[0]}", json={"order": 1})
    assert patch.status_code == 200
    assert patch.json()["order"] == 1

    # Fetch all notes and verify new order
    res = client.get("/notes/")
    ordered = [n["detail"] for n in res.json()]
    assert ordered == ["Note 1", "Note 3", "Note 2"]


def test_patch_multiple_update_types_fails(client):
    """
    Mixing order + detail in a patch request should fail.
    """
    res = client.post("/notes/", json={"detail": "Multi update"})
    note_id = res.json()["id"]

    patch = client.patch(f"/notes/{note_id}", json={"order": 2, "detail": "New detail"})
    assert patch.status_code == 400
    assert "Only one type of update" in patch.json()["detail"]


def test_delete_note_and_reorder_remaining(client):
    """
    Deleting a note should reorder remaining notes to fill the gap.
    """
    # Create 3 notes
    ids = []
    for i in range(3):
        res = client.post("/notes/", json={"detail": f"Note {i+1}"})
        ids.append(res.json()["id"])

    # Delete second note (order 2)
    delete = client.delete(f"/notes/{ids[1]}")
    assert delete.status_code == 200

    # Get notes and check order shifted
    res = client.get("/notes/")
    data = res.json()
    assert len(data) == 2
    assert data[0]["order"] == 1
    assert data[1]["order"] == 2
