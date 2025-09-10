from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import controllers
from controller.NewsController import news_router

# Create FastAPI application
app = FastAPI(
    title="News API Backend",
    description="Backend API for news articles management",
    version="1.0.0"
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
        "message": "News API Backend is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend services are operational"
    }

# Include routers
app.include_router(news_router, prefix="", tags=["News"])

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ApplicationBackend:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )