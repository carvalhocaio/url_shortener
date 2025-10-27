from fastapi import FastAPI

from app.api.routes import admin, urls

# Initialize FastAPI application
# Note: Database migrations are now managed by Alembic
# Run 'make migrate' to apply pending migrations
app = FastAPI()

# Include routers
app.include_router(urls.router)
app.include_router(admin.router)
