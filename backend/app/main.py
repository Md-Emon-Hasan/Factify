import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logger import setup_logging
from app.api import endpoints
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logger = setup_logging()


def warm_up_model():
    # TensorFlow traces its graph on the first predict() call, so absorb
    # that cost at startup instead of making the first user wait
    if not settings.MODEL_WARMUP_ENABLED:
        logger.info("Model warm-up disabled, skipping")
        return

    try:
        logger.info("Model warm-up starting...")
        started = time.perf_counter()

        from app.services.prediction import detector
        detector.predict(settings.MODEL_WARMUP_TEXT)

        elapsed = time.perf_counter() - started
        logger.info(f"Model warm-up completed in {elapsed:.2f}s")
    except Exception as e:
        logger.error(f"Model warm-up failed: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    warm_up_model()
    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A monolithic AI-powered Fact Checking application",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    client = request.client.host if request.client else "unknown"
    logger.warning(
        f"Rate limit exceeded for {client} on {request.url.path}"
    )
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again shortly."},
        headers={"Retry-After": "60"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    # Flatten pydantic's messages into one readable string, keeping the
    # original list under "errors"
    errors = exc.errors()
    messages = [
        str(err.get("msg", "")).replace("Value error, ", "")
        for err in errors
    ]
    detail = " ".join(m for m in messages if m) or "Invalid request."
    logger.info(f"Validation failed on {request.url.path}: {detail}")
    return JSONResponse(
        status_code=422,
        content={"detail": detail, "errors": jsonable_errors(errors)},
    )


def jsonable_errors(errors):
    cleaned = []
    for err in errors:
        cleaned.append({
            "loc": [str(part) for part in err.get("loc", [])],
            "msg": str(err.get("msg", "")),
            "type": str(err.get("type", "")),
        })
    return cleaned


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
