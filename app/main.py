from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logging
from app.api import endpoints
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A monolithic AI-powered Fact Checking application",
)

# Include routers
app.include_router(endpoints.router)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://factify-frontend.vercel.app", # Add Vercel domain placeholder
    "*", # Allow all for now to ensure smooth deployment testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Factify API is running. Access docs at /docs"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
