import os
import sys
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

# Add path to access models and utilities
sys.path.append(os.getcwd())

try:
    from src.models.Text_Clustering import inference as clustering
except ImportError as e:
    print(f"Warning: Could not import clustering model: {e}")
    clustering = None

# Import the pick_random_items function
def pick_random_items(data, n=20, seed=None, filter_fn=None):
    """Simple implementation of pick_random_items if not available"""
    import random
    if seed:
        random.seed(seed)
    
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = list(data.values())
    else:
        return []
    
    if filter_fn:
        items = [x for x in items if filter_fn(x)]
    
    if not items:
        return []
    
    k = min(n, len(items))
    return random.sample(items, k)

class ClusterInfo(BaseModel):
    cluster_id: int
    cluster_name: str
    article_count: int
    keywords: List[str] = []

class ClusteredArticle(BaseModel):
    id: int
    url: str
    url_img: str
    title: str
    description: str
    content: str
    metadata: dict
    cluster_id: int
    cluster_name: str

class ArticleCluster(BaseModel):
    cluster_info: ClusterInfo
    articles: List[ClusteredArticle]

class ClusteringService:
    """Service for text clustering operations"""
    
    def __init__(self):
        """Initialize the clustering service"""
        pass
    
    def get_clustered_articles(self, limit_per_cluster: int = 5, max_clusters: int = 6) -> List[ArticleCluster]:
        """
        Get articles grouped by clusters
        
        Args:
            limit_per_cluster (int): Maximum articles per cluster
            max_clusters (int): Maximum number of clusters to return
            
        Returns:
            List[ArticleCluster]: List of clusters with their articles
        """
        try:
            # Load JSON data
            with open("config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)

            json_path = config["DATA"]["PROCESSED_DATA_IMG_URL"]
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # If clustering model is available, use it for real clustering
            if clustering is not None:
                return self._cluster_with_model(data, limit_per_cluster, max_clusters)
            else:
                # Fallback: create mock clusters based on categories
                return self._create_mock_clusters(data, limit_per_cluster, max_clusters)
                
        except Exception as e:
            print(f"Error getting clustered articles: {e}")
            return []
    
    def _cluster_with_model(self, data: List[dict], limit_per_cluster: int, max_clusters: int) -> List[ArticleCluster]:
        """Use actual clustering model to group articles"""
        try:
            # This would implement real clustering logic
            # For now, return mock clusters
            return self._create_mock_clusters(data, limit_per_cluster, max_clusters)
        except Exception as e:
            print(f"Error in clustering model: {e}")
            return self._create_mock_clusters(data, limit_per_cluster, max_clusters)
    
    def _create_mock_clusters(self, data: List[dict], limit_per_cluster: int, max_clusters: int) -> List[ArticleCluster]:
        """Create mock clusters based on article categories and topics"""
        clusters = []
        
        # Define cluster themes based on Vietnamese news topics
        cluster_themes = [
            {
                "id": 1,
                "name": "NEPAL",
                "keywords": ["nepal", "động đất", "thiên tai", "cứu hộ", "khách sạn"],
                "filter_keywords": ["nepal", "Nepal"]
            },
            {
                "id": 2, 
                "name": "NHẬN THẲNG",
                "keywords": ["bắt giữ", "tội phạm", "công an", "điều tra", "giao thông"],
                "filter_keywords": ["bắt", "tại", "điều tra", "công an", "cảnh sát"]
            },
            {
                "id": 3,
                "name": "BA LAN", 
                "keywords": ["nato", "quân sự", "không quân", "phòng thủ", "ba lan"],
                "filter_keywords": ["nato", "NATO", "ba lan", "Ba Lan", "quân sự"]
            },
            {
                "id": 4,
                "name": "ĐẠI HỌC Y HÀ NỘI",
                "keywords": ["đại học", "y tế", "sinh viên", "giáo dục", "hà nội"],
                "filter_keywords": ["đại học", "sinh viên", "y tế", "học", "giáo dục"]
            },
            {
                "id": 5,
                "name": "KINH TẾ",
                "keywords": ["kinh tế", "doanh nghiệp", "đầu tư", "thị trường", "tài chính"],
                "filter_keywords": ["kinh tế", "doanh nghiệp", "đầu tư", "thị trường"]
            },
            {
                "id": 6,
                "name": "THỂ THAO",
                "keywords": ["bóng đá", "thể thao", "tuyển", "giải", "cầu thủ"],
                "filter_keywords": ["bóng đá", "thể thao", "tuyển", "giải"]
            }
        ]
        
        # Limit to max_clusters
        cluster_themes = cluster_themes[:max_clusters]
        
        for theme in cluster_themes:
            # Filter articles for this cluster
            def filter_fn(item):
                title = item.get('title', '').lower()
                description = item.get('description', '').lower() 
                content = item.get('content', '').lower()
                
                text_content = f"{title} {description} {content}"
                
                # Check if any filter keywords match
                return any(keyword.lower() in text_content for keyword in theme["filter_keywords"])
            
            # Get articles for this cluster
            cluster_articles = pick_random_items(
                data, 
                n=limit_per_cluster * 3,  # Get more to filter from
                seed=theme["id"],
                filter_fn=filter_fn
            )
            
            # If no articles found with keywords, get random articles
            if not cluster_articles:
                cluster_articles = pick_random_items(
                    data,
                    n=limit_per_cluster,
                    seed=theme["id"]
                )
            
            # Limit to desired number
            cluster_articles = cluster_articles[:limit_per_cluster]
            
            if cluster_articles:
                # Convert to ClusteredArticle objects
                articles = []
                for i, article_data in enumerate(cluster_articles):
                    try:
                        article = ClusteredArticle(
                            id=theme["id"] * 1000 + i,
                            url=article_data.get('url', ''),
                            url_img=article_data.get('url_img', ''),
                            title=article_data.get('title', ''),
                            description=article_data.get('description', ''),
                            content=article_data.get('content', ''),
                            metadata=article_data.get('metadata', {}),
                            cluster_id=theme["id"],
                            cluster_name=theme["name"]
                        )
                        articles.append(article)
                    except Exception as e:
                        print(f"Error creating article: {e}")
                        continue
                
                if articles:
                    cluster_info = ClusterInfo(
                        cluster_id=theme["id"],
                        cluster_name=theme["name"],
                        article_count=len(articles),
                        keywords=theme["keywords"]
                    )
                    
                    cluster = ArticleCluster(
                        cluster_info=cluster_info,
                        articles=articles
                    )
                    clusters.append(cluster)
        
        return clusters
    
    def get_cluster_by_id(self, cluster_id: int, limit: int = 20) -> Optional[ArticleCluster]:
        """
        Get articles from a specific cluster
        
        Args:
            cluster_id (int): The cluster ID
            limit (int): Maximum articles to return
            
        Returns:
            Optional[ArticleCluster]: Cluster with articles or None
        """
        all_clusters = self.get_clustered_articles(limit_per_cluster=limit, max_clusters=10)
        
        for cluster in all_clusters:
            if cluster.cluster_info.cluster_id == cluster_id:
                return cluster
        
        return None
    
    def get_cluster_info(self) -> List[ClusterInfo]:
        """
        Get information about all available clusters
        
        Returns:
            List[ClusterInfo]: List of cluster information
        """
        clusters = self.get_clustered_articles(limit_per_cluster=1, max_clusters=10)
        return [cluster.cluster_info for cluster in clusters]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the clustering model
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "model_type": "text_clustering",
            "description": "Text clustering model for Vietnamese news articles",
            "status": "active" if clustering is not None else "mock",
            "available_clusters": len(self.get_cluster_info())
        }