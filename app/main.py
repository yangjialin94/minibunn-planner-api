from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ENV, WEB_URL
from app.core.database import Base
from app.routes import journals, notes, stripe, tasks, users
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
if ENV == "dev":
    allow_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    allow_origins = [WEB_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 ENV:", ENV)
print("✅ Allowing origins:", allow_origins)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(journals.router, prefix="/journals", tags=["journals"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(stripe.router, prefix="/api/stripe", tags=["stripe"])
