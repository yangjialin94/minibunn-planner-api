from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine, get_db
from app.core.init_db import init_test_data
from app.routes import journals, tasks
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models to register them with Base
    from app.models import journal, task, user

    # Recreate database schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Load test data
    db = next(get_db())
    try:
        init_test_data(db)
    finally:
        db.close()

    # Initialize the scheduler
    start_scheduler()

    yield  # App startup complete


# Attach lifespan here
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
