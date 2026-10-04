"""
GovFlow AI — FastAPI Application
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from app.routers import services, chat, admin, auth, feedback, history
from app.rate_limit import limiter

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Comma-separated list, e.g. "http://localhost:3000,https://govflow.lk"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app = FastAPI(
    title="GovFlow AI API",
    description="Backend API for GovFlow AI — Sri Lankan citizen service guidance platform",
    version="0.1.0",
)

# Rate limiting: routes opt in with @limiter.limit(...); over-limit requests get HTTP 429
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allows the Next.js frontend (on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "GovFlow AI API"}
