"""FastAPI application entry point for Smart Data Quality Analyzer."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.routes.health import router as health_router
from app.routes.analyze import router as analyze_router
from app.routes.clean import router as clean_router
from app.routes.reports import router as reports_router
from app.routes.download import router as download_router

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sdqa_backend")

app = FastAPI(
    title="Smart Data Quality Analyzer API",
    description="Explainable, automated data quality assessment and interactive dataset cleaning engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler to prevent exposing server internal paths
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing the dataset. Please verify the file structure."}
    )

# Include routers
app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(clean_router)
app.include_router(reports_router)
app.include_router(download_router)


@app.get("/")
def root():
    return {
        "message": "Smart Data Quality Analyzer API is active.",
        "documentation": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
