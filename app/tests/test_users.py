def test_patch_user_success(seeded_client):
    res = seeded_client.patch(
        "/users/1",
        json={"name": "Updated Name"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"


def test_patch_user_not_found(client):
    """
    Tests updating a user that doesn't exist.
    """
    res = client.patch(
        "/users/9999",
        json={"name": "Ghost"},
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"
