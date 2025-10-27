from fastapi import FastAPI

from app.api.routes import admin, urls
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

# Include routers
app.include_router(urls.router)
app.include_router(admin.router)
