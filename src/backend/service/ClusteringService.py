import os
import sys
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Add path to access models and utilities
sys.path.append(os.getcwd())
from src.utils.RandomText import pick_random_items

try:
    from src.models.Text_Clustering.Text_cluster import VietnameseTextClustering
except ImportError as e:
    print(f"Warning: Could not import VietnameseTextClustering: {e}")
    VietnameseTextClustering = None

try:
    from src.backend.service.OpenAIService import OpenAIService
except ImportError as e:
    print(f"Warning: Could not import OpenAIService: {e}")
    OpenAIService = None


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
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            print("🚀 Creating ClusteringService singleton instance")
            cls._instance = super(ClusteringService, cls).__new__(cls)
        else:
            print("♻️ Reusing existing ClusteringService singleton")
        return cls._instance
    
    def __init__(self):
        """Initialize the clustering service only once"""
        if not ClusteringService._initialized:
            print(f"🚀 Initializing ClusteringService singleton (this should only happen once)... in in PID={os.getpid()}")
            self._clustering_model = VietnameseTextClustering()
            self.openai_service = self._get_openai_service()
            ClusteringService._initialized = True
            print("✅ ClusteringService singleton initialized successfully!")
        else:
            print(f"♻️ Reusing ClusteringService in PID={os.getpid()}")
    
    def _get_openai_service(self):
        """Get OpenAI service instance (lazy initialization)"""
        print("Initializing OpenAI service...")
        return OpenAIService()
    
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
            if self._clustering_model is not None:
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
            # Get sample clusters from the model
            sample_data = self._clustering_model.sample_clusters(
                n_clusters=max_clusters,
                k_nearest=limit_per_cluster
            )

            # Group articles by cluster_id
            cluster_dict = {}
            for article_data in sample_data:
                cluster_id = article_data.get('cluster_id', 0)
                if cluster_id not in cluster_dict:
                    cluster_dict[cluster_id] = []
                cluster_dict[cluster_id].append(article_data)

            # Convert to ArticleCluster objects
            clusters = []
            cluster_articles_for_labeling = {}

            for cluster_id, articles_data in cluster_dict.items():
                articles = []
                for i, article_data in enumerate(articles_data):
                    try:
                        # Ensure all string fields have default values and are not None
                        article = ClusteredArticle(
                            id=cluster_id * 1000 + i,
                            url=article_data.get('url') or '',
                            url_img=article_data.get('url_img') or 'https://via.placeholder.com/120x96?text=📰&bg=f3f4f6',
                            title=article_data.get('title') or 'Untitled',
                            description=article_data.get('description') or '',
                            content=article_data.get('content') or '',
                            metadata=article_data.get('metadata') or {},
                            cluster_id=cluster_id,
                            cluster_name=f"Cluster {cluster_id}"
                        )
                        articles.append(article)
                    except Exception as e:
                        print(f"Error creating article: {e}")
                        continue

                if articles:
                    # Store articles data for OpenAI labeling
                    cluster_articles_for_labeling[cluster_id] = articles_data

                    cluster_info = ClusterInfo(
                        cluster_id=cluster_id,
                        cluster_name=f"Cluster {cluster_id}",
                        article_count=len(articles),
                        keywords=[]
                    )

                    cluster = ArticleCluster(
                        cluster_info=cluster_info,
                        articles=articles
                    )
                    clusters.append(cluster)

            # Generate cluster labels using OpenAI
            try:
                if self.openai_service and self.openai_service.is_available():
                    print("Generate label for clusters with openai")
                    for cluster in clusters:
                        cluster_id = cluster.cluster_info.cluster_id
                        if cluster_id in cluster_articles_for_labeling:
                            # Generate label using OpenAI
                            label = self.openai_service.generate_cluster_label(
                                cluster_articles_for_labeling[cluster_id], 
                                max_words=5
                            )
                            # Update cluster info with generated label
                            cluster.cluster_info.cluster_name = label
                            # Also update all articles in this cluster
                            for article in cluster.articles:
                                article.cluster_name = label

            except Exception as e:
                print(f"Error generating OpenAI labels: {e}")
                # Continue with default cluster names if OpenAI fails

            return clusters
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
                        # Ensure all string fields have default values and are not None
                        article = ClusteredArticle(
                            id=theme["id"] * 1000 + i,
                            url=article_data.get('url') or '',
                            url_img=article_data.get('url_img') or 'https://via.placeholder.com/120x96?text=📰&bg=f3f4f6',
                            title=article_data.get('title') or 'Untitled',
                            description=article_data.get('description') or '',
                            content=article_data.get('content') or '',
                            metadata=article_data.get('metadata') or {},
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
    
# Global instance
_service_instance = None

def get_clustering_service():
    """Return the singleton instance of ClusteringService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ClusteringService()
    return _service_instance

async def initialize_clustering_on_startup():
    """Initialize clustering model and run initial clustering on app startup"""
    try:
        # Get the singleton service
        service = get_clustering_service()
        
        # Pre-warm the clustering model by running sample_clusters
        if service._clustering_model is not None:
            print("🔥 Pre-warming clustering model...")
            # This will trigger the fit_predict if not already fitted
            sample_clusters = service.get_clustered_articles(max_clusters=6, limit_per_cluster=4)
            print(f"✅ Clustering pre-warmed successfully! Generated {len(sample_clusters)} sample clusters")
        else:
            print("⚠️ Clustering model not available, skipping pre-warming")
            
    except Exception as e:
        print(f"Error during clustering initialization: {e}")
        # Don't fail the entire app startup if clustering fails
        pass