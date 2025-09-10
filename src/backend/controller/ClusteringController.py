from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add service path
sys.path.append(os.getcwd())
from src.backend.service.ClusteringService import ClusteringService, ArticleCluster, ClusterInfo

# Create router for clustering endpoints
clustering_router = APIRouter()

# Response models
class ClustersResponse(BaseModel):
    clusters: List[ArticleCluster]
    total_clusters: int

class ClusterResponse(BaseModel):
    cluster: ArticleCluster

class ClusterInfoResponse(BaseModel):
    clusters: List[ClusterInfo]

class ModelInfoResponse(BaseModel):
    model_info: Dict[str, Any]

# Initialize service
clustering_service = ClusteringService()

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

@clustering_router.get("/api/clusters/{cluster_id}", response_model=ClusterResponse)
async def get_cluster_by_id(
    cluster_id: int,
    limit: int = Query(default=20, ge=1, le=50, description="Maximum articles to return")
):
    """
    Get articles from a specific cluster
    
    Parameters:
    - cluster_id: The cluster ID
    - limit: Maximum articles to return (1-50)
    
    Returns:
    - Cluster with articles
    """
    try:
        cluster = clustering_service.get_cluster_by_id(cluster_id, limit)
        
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        return ClusterResponse(cluster=cluster)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering error: {str(e)}")

@clustering_router.get("/api/clusters/info", response_model=ClusterInfoResponse)
async def get_cluster_info():
    """
    Get information about all available clusters
    
    Returns:
    - List of cluster information
    """
    try:
        cluster_info = clustering_service.get_cluster_info()
        return ClusterInfoResponse(clusters=cluster_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cluster info: {str(e)}")

@clustering_router.get("/api/clustering/model-info", response_model=ModelInfoResponse)
async def get_clustering_model_info():
    """
    Get information about the clustering model
    
    Returns:
    - Model information
    """
    try:
        model_info = clustering_service.get_model_info()
        return ModelInfoResponse(model_info=model_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

# Additional endpoint for hot news (featured clusters)
@clustering_router.get("/api/hot-news", response_model=ClustersResponse)
async def get_hot_news(
    limit_per_cluster: int = Query(default=4, ge=1, le=10, description="Articles per cluster for hot news"),
    featured_clusters: int = Query(default=4, ge=1, le=8, description="Number of featured clusters")
):
    """
    Get hot news articles grouped by featured clusters
    
    This endpoint is specifically designed for the hot news page
    
    Parameters:
    - limit_per_cluster: Articles per cluster (1-10)  
    - featured_clusters: Number of featured clusters (1-8)
    
    Returns:
    - Featured clusters with articles optimized for hot news display
    """
    try:
        clusters = clustering_service.get_clustered_articles(
            limit_per_cluster=limit_per_cluster,
            max_clusters=featured_clusters
        )
        
        return ClustersResponse(
            clusters=clusters,
            total_clusters=len(clusters)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hot news error: {str(e)}")

# Legacy endpoint for backward compatibility
@clustering_router.get("/clusters", response_model=List[ArticleCluster])
async def get_clusters_legacy(
    limit_per_cluster: int = Query(default=5, ge=1, le=20),
    max_clusters: int = Query(default=6, ge=1, le=10)
):
    """
    Legacy endpoint for getting clustered articles
    
    Returns raw cluster data for backward compatibility
    """
    try:
        clusters = clustering_service.get_clustered_articles(
            limit_per_cluster=limit_per_cluster,
            max_clusters=max_clusters
        )
        
        return clusters
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")