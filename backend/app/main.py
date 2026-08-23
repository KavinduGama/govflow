"""
GovFlow AI — FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import services, chat, admin, auth, feedback, history

app = FastAPI(
    title="GovFlow AI API",
    description="Backend API for GovFlow AI — Sri Lankan citizen service guidance platform",
    version="0.1.0",
)

# CORS — allows the Next.js frontend (on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
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
