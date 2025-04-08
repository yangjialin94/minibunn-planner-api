from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ENV, WEB_URL
from app.core.database import Base, engine, get_db
from app.core.init_db import init_test_data
from app.routes import journals, tasks, users
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models to register them with Base
    from app.models import journal, task, user

    # Initialize the scheduler
    start_scheduler()

    yield  # App startup complete


# Attach lifespan here
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])
