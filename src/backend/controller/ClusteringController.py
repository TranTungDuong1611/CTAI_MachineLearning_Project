from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add service path
sys.path.append(os.getcwd())
from src.backend.service.ClusteringService import get_clustering_service, ArticleCluster

# Create router for clustering endpoints
clustering_router = APIRouter()

# Response models
class ClustersResponse(BaseModel):
    clusters: List[ArticleCluster]
    total_clusters: int

# API Routes
@clustering_router.get("/api/clusters", response_model=ClustersResponse)
async def get_clustered_articles(
    limit_per_cluster: int = Query(default=5, ge=1, le=20, description="Maximum articles per cluster"),
    max_clusters: int = Query(default=6, ge=1, le=10, description="Maximum number of clusters to return")
):
    """
    Get articles grouped by clusters
    
    Parameters:
    - limit_per_cluster: Maximum articles per cluster (1-20)
    - max_clusters: Maximum number of clusters to return (1-10)
    
    Returns:
    - List of clusters with their articles
    """
    try:
        clustering_service = get_clustering_service() 
        clusters = clustering_service.get_clustered_articles(
            limit_per_cluster=limit_per_cluster,
            max_clusters=max_clusters
        )
        
        return ClustersResponse(
            clusters=clusters,
            total_clusters=len(clusters)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering error: {str(e)}")