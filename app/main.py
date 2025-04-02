from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine, get_db
from app.core.init_db import init_test_data
from app.routes import journals, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models to register them with Base
    from models import journal, task, user

    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Load test data
    db = next(get_db())
    try:
        init_test_data(db)
    finally:
        db.close()

    # Yield control to the app
    yield


# Create FastAPI instance
app = FastAPI()

# Include routers
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
