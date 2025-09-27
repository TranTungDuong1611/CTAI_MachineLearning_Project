import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Set environment variable to avoid tokenizers warnings during forking
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add the backend directory to Python path for imports
sys.path.append(os.getcwd())

# Import controllers
from controller.NewsController import news_router
from controller.ClassificationController import classification_router
from controller.ClusteringController import clustering_router
from controller.SummationController import summarization_router

# Import clustering initialization
from src.backend.service.ClusteringService import initialize_clustering_on_startup

# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌟 FastAPI application starting up...")
    await initialize_clustering_on_startup()
    print("🎉 Startup initialization complete!")
    yield
    # Shutdown (if needed)
    print("🔄 FastAPI application shutting down...")

# Create FastAPI application
app = FastAPI(
    title="News & AI API Backend",
    description="Backend API for news articles management, text classification, and summarization",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "News & AI API Backend is running",
        "version": "1.0.0",
        "services": [
            "News Articles Management",
            "Text Classification", 
            "Text Clustering",
            "Text Summarization"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "All backend services are operational",
        "services": {
            "news": "active",
            "classification": "active",
            "clustering": "active", 
            "summarization": "active"
        }
    }

# Include routers
app.include_router(news_router, prefix="", tags=["News"])
app.include_router(classification_router, prefix="", tags=["Text Classification"])
app.include_router(clustering_router, prefix="", tags=["Text Clustering"])
app.include_router(summarization_router, prefix="", tags=["Text Summarization"])

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "ApplicationBackend:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False,
        log_level="info"
    )