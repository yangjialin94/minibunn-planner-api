import os

"""
Script to initialize test data in the database.
"""
if os.getenv("ENV") == "development":
    db = next(get_db())
    try:
        init_test_data(db)
    finally:
        db.close()
