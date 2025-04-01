from core.database import Base, engine, get_db
from core.init_db import init_test_data
from fastapi import FastAPI
from routes import journals, tasks

# Create FastAPI instance
app = FastAPI()

# Include routers
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


# Create tables
@app.on_event("startup")
async def startup_event():
    from models import journal, task, user

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Load test data
    db = next(get_db())
    try:
        init_test_data(db)
    finally:
        db.close()
