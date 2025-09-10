from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service.NewService import NewsService, NewsArticle

# Create router for news endpoints
news_router = APIRouter()

# Response models
class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total: int
    page: int
    limit: int

# Request models
class CreateNewsRequest(BaseModel):
    url: str
    url_img: str
    title: str
    description: str
    content: str
    metadata: dict

class UpdateNewsRequest(BaseModel):
    url: Optional[str] = None
    url_img: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

# Initialize service
news_service = NewsService()

# API Routes
@news_router.get("/api/news", response_model=List[NewsArticle])
async def get_news(
    limit: int = 20,
    page: int = 1,
    category: Optional[str] = None
):
    """
    Get news articles from JSON data
    
    Parameters:
    - limit: Number of articles to return (default: 20, max: 100)
    - page: Page number for pagination (default: 1)
    - category: Filter by category (optional)
    
    Returns:
    - List of news articles
    """
    try:
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        if page < 1:
            page = 1
        
        # Get articles from JSON using get_random_news_from_json
        articles, total = news_service.get_random_news_from_json(limit=limit, category=category)
        
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.get("/api/news/paginated", response_model=NewsResponse)
async def get_news_paginated(
    limit: int = 20,
    page: int = 1,
    category: Optional[str] = None
):
    """
    Get news articles with pagination info
    
    Returns:
    - List of articles with pagination metadata
    """
    try:
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        if page < 1:
            page = 1
            
        offset = (page - 1) * limit
        
        # Get articles from service
        articles, total = news_service.get_random_news_from_json(limit=limit, category=category, seed=42)
        
        return NewsResponse(
            articles=articles,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.get("/api/news/categories")
async def get_categories():
    """Get all available news categories"""
    try:
        categories = news_service.get_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.get("/api/news/{news_id}", response_model=NewsArticle)
async def get_news_by_id(news_id: int):
    """Get a single news article by ID"""
    try:
        article = news_service.get_news_by_id(news_id)
        if not article:
            raise HTTPException(status_code=404, detail="News article not found")
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.post("/api/news", response_model=NewsArticle)
async def create_news(news_data: CreateNewsRequest):
    """Create a new news article"""
    try:
        article = news_service.create_news(
            url=news_data.url,
            url_img=news_data.url_img,
            title=news_data.title,
            description=news_data.description,
            content=news_data.content,
            metadata=news_data.metadata
        )
        return article
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.put("/api/news/{news_id}", response_model=NewsArticle)
async def update_news(news_id: int, news_data: UpdateNewsRequest):
    """Update an existing news article"""
    try:
        article = news_service.update_news(
            news_id=news_id,
            url=news_data.url,
            url_img=news_data.url_img,
            title=news_data.title,
            description=news_data.description,
            content=news_data.content,
            metadata=news_data.metadata
        )
        if not article:
            raise HTTPException(status_code=404, detail="News article not found")
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@news_router.delete("/api/news/{news_id}")
async def delete_news(news_id: int):
    """Delete a news article"""
    try:
        success = news_service.delete_news(news_id)
        if not success:
            raise HTTPException(status_code=404, detail="News article not found")
        return {"message": "News article deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")