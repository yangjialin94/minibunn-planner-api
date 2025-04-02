from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine, get_db
from app.core.init_db import init_test_data
from app.routes import journals, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models to register them with Base
    from app.models import journal, task, user  # make sure these are app.models.XXX

    # Recreate database schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Load test data
    db = next(get_db())
    try:
        init_test_data(db)
    finally:
        db.close()

    yield  # App startup complete


# Attach lifespan here
app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
