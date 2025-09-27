import json
import sys
import os
import sqlite3
from typing import List, Optional
from pydantic import BaseModel
from src.utils.RandomText import pick_random_items

# Add utils directory to path
sys.path.append(os.getcwd())

class ArticleMetadata(BaseModel):
    cat: Optional[str] = None
    subcat: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None

class RandomArticle(BaseModel):
    id: Optional[int] = None
    url: str
    url_img: str
    title: str
    description: str
    content: str
    metadata: ArticleMetadata
    title_clean: Optional[str] = None
    desc_clean: Optional[str] = None
    content_clean: Optional[str] = None

# For compatibility with existing NewsArticle structure
class NewsArticle(BaseModel):
    id: int
    title: str
    source: str
    time: str
    views: str
    thumbnail: str
    category: str

class RandomTextService:
    def __init__(self, database_path: str = "news.db", json_file_path: Optional[str] = None):
        self.database_path = database_path
        self.json_file_path = json_file_path or "data/processed_data/processed_data_dash.json"
        self.data = None
        self._load_data()
        self._init_database()

    def _load_data(self):
        """Load data from JSON file if it exists"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"Loaded {len(self.data)} articles from JSON file")
            else:
                print(f"JSON file not found at {self.json_file_path}, will use database only")
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            self.data = None

    def _init_database(self):
        """Initialize database for storing random articles"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS random_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                url_img TEXT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                category TEXT,
                subcategory TEXT,
                published_date TEXT,
                author TEXT,
                title_clean TEXT,
                desc_clean TEXT,
                content_clean TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_random_articles_from_json(self, n: int = 10, category: Optional[str] = None, 
                                    seed: Optional[int] = None) -> List[RandomArticle]:
        """Get random articles from JSON data"""
        if not self.data:
            return []

        filter_fn = None
        if category:
            filter_fn = lambda x: x.get('metadata', {}).get('cat', '').lower() == category.lower()

        try:
            random_items = pick_random_items(
                self.data, 
                n=n, 
                seed=seed, 
                allow_repeat=False, 
                filter_fn=filter_fn
            )
            
            articles = []
            for item in random_items:
                try:
                    metadata = ArticleMetadata(**item.get('metadata', {}))
                    article = RandomArticle(
                        url=item.get('url', ''),
                        url_img=item.get('url_img', ''),
                        title=item.get('title', ''),
                        description=item.get('description', ''),
                        content=item.get('content', ''),
                        metadata=metadata,
                        title_clean=item.get('title_clean'),
                        desc_clean=item.get('desc_clean'),
                        content_clean=item.get('content_clean')
                    )
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
                    
            return articles
        except Exception as e:
            print(f"Error getting random articles: {e}")
            return []

    def convert_to_news_format(self, articles: List[RandomArticle]) -> List[NewsArticle]:
        """Convert RandomArticle format to NewsArticle format for compatibility"""
        news_articles = []
        for i, article in enumerate(articles):
            try:
                # Extract category from metadata
                category = article.metadata.cat or "MỚI"
                category_map = {
                    "sức khỏe": "NÓNG",
                    "thể thao": "THỂ THAO",
                    "kinh tế": "NÓNG",
                    "chính trị": "NÓNG",
                    "xã hội": "MỚI",
                    "giáo dục": "MỚI",
                    "công nghệ": "NÓNG",
                    "du lịch": "MỚI"
                }
                mapped_category = category_map.get(category.lower(), "MỚI")
                
                # Extract source from URL or metadata
                source = article.metadata.author or "VietnamNet"
                
                # Generate time from published_date or use default
                time_str = article.metadata.published_date or "Vài giờ trước"
                if "/" in time_str:
                    time_str = "Vài giờ trước"
                
                # Generate views (random for display purposes)
                import random
                views = f"{random.randint(50, 2000)} lượt xem"
                
                news_article = NewsArticle(
                    id=1000 + i,  # Start from 1000 to avoid conflicts
                    title=article.title,
                    source=source,
                    time=time_str,
                    views=views,
                    thumbnail=article.url_img,
                    category=mapped_category
                )
                news_articles.append(news_article)
            except Exception as e:
                print(f"Error converting article to news format: {e}")
                continue
                
        return news_articles

    def save_articles_to_database(self, articles: List[RandomArticle]):
        """Save random articles to database"""
        if not articles:
            return
            
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        for article in articles:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO random_articles 
                    (url, url_img, title, description, content, category, subcategory, 
                     published_date, author, title_clean, desc_clean, content_clean)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.url,
                    article.url_img,
                    article.title,
                    article.description,
                    article.content,
                    article.metadata.cat,
                    article.metadata.subcat,
                    article.metadata.published_date,
                    article.metadata.author,
                    article.title_clean,
                    article.desc_clean,
                    article.content_clean
                ))
            except Exception as e:
                print(f"Error saving article to database: {e}")
                continue
        
        conn.commit()
        conn.close()

    def get_random_news_articles(self, limit: int = 10, category: Optional[str] = None, 
                                seed: Optional[int] = None) -> List[NewsArticle]:
        """Get random articles in NewsArticle format"""
        # Get random articles from JSON
        random_articles = self.get_random_articles_from_json(n=limit, category=category, seed=seed)
        
        # Convert to news format
        news_articles = self.convert_to_news_format(random_articles)
        
        # Save to database for future reference
        if random_articles:
            self.save_articles_to_database(random_articles)
        
        return news_articles

    def get_available_categories(self) -> List[str]:
        """Get available categories from JSON data"""
        if not self.data:
            return ["MỚI", "NÓNG", "THỂ THAO"]
            
        categories = set()
        for item in self.data:
            cat = item.get('metadata', {}).get('cat')
            if cat:
                categories.add(cat)
        
        return sorted(list(categories))