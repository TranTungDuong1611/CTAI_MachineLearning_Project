import os
import json
import random
import sqlite3
from typing import List, Optional, Tuple
from pydantic import BaseModel
from .RandomTextService import RandomTextService, RandomArticle
from typing import Mapping, Sequence, Callable, Any, List, Tuple, Union
import json

Item = Any
MaybeKeyed = Union[Item, Tuple[Any, Item]]

def pick_random_items(
    data: Union[Sequence[Item], Mapping[Any, Item]],
    n: int = 20,
    allow_repeat: bool = False,
    filter_fn: Callable[[Item], bool] | None = None,
    keep_keys: bool = False
) -> List[MaybeKeyed]:
    rng = random.Random()
    if isinstance(data, Mapping):
        items: List[MaybeKeyed] = list(data.items()) if keep_keys else list(data.values())
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
        items = list(data)
    else:
        raise TypeError("data phải là list hoặc dict")
    if filter_fn is not None:
        if isinstance(data, Mapping) and keep_keys:
            items = [(k, v) for (k, v) in items if filter_fn(v)]
        else:
            items = [x for x in items if filter_fn(x)]

    if not items:
        return []
    if allow_repeat:
        return [rng.choice(items) for _ in range(n)]
    else:
        k = min(n, len(items))
        return rng.sample(items, k)

class NewsArticle(BaseModel):
    id: int
    url: str
    url_img: str
    title: str
    description: str
    content: str
    metadata: dict

class NewsService:
    def __init__(self, database_path: str = "news.db"):
        self.database_path = database_path
        self.random_service = RandomTextService(database_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with sample data if it doesn't exist"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                time TEXT NOT NULL,
                views TEXT NOT NULL,
                thumbnail TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if table is empty, if so, add sample data
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Sample data
            sample_articles = [
                ("Thủ tướng Campuchia gửi lời tới tân Thủ tướng Thái Lan", "TTXVN", "2 giờ", "1013 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "NÓNG"),
                
                ("Giá vàng khó bứt phá mạnh nữa, không nên mua đuổi theo thị trường", "VietNamNet", "3 giờ", "3152 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "NÓNG"),
                
                ("Điều ông Trump lo lắng nhất", "ZNEWS", "3 giờ", "1233 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "MỚI"),
                
                ("Bắt Mạnh 'Gà' - triệt xóa tận gốc băng nhóm Vi 'Ngô' ở Thanh Hóa", "Công an nhân dân", "22 phút", "142 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "NÓNG"),
                
                ("Vòng loại U23 châu Á: Tuyển Việt Nam quyết thắng Yemen để đi tiếp với ngôi đầu", "VietnamPlus", "27 phút", "203 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "THỂ THAO"),
                
                ("Tuyển Anh thắng dễ trước 'tí hon' Andorra", "Người Lao Động", "1 giờ", "1 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "THỂ THAO"),
                
                ("Thông tin mới về vụ tai nạn giao thông nghiêm trọng tại Hà Nội", "Tuổi Trẻ", "45 phút", "892 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "MỚI"),
                
                ("Dự báo thời tiết hôm nay: Miền Bắc có mưa rào và dông", "VnExpress", "1 giờ", "456 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "MỚI"),
                
                ("Chính phủ thông qua chính sách hỗ trợ doanh nghiệp nhỏ và vừa", "Báo Đầu tư", "30 phút", "678 lượt xem", 
                "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw", "NÓNG"),
            ]
            
            cursor.executemany('''
                INSERT INTO news_articles (title, source, time, views, thumbnail, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_articles)
        
        conn.commit()
        conn.close()

    def get_news(self, limit: int = 20, offset: int = 0, category: Optional[str] = None) -> Tuple[List[NewsArticle], int]:
        """Get news articles using random selection from JSON data"""
        try:
            # Try to get random articles from JSON first
            articles, total = self.get_random_news_from_json(limit=limit, category=category, seed=42)
            return articles, total
        except Exception as e:
            print(f"Error getting random news, falling back to database: {e}")
            # Fallback to database if JSON method fails
            return self._get_news_from_database(limit, offset, category)
    
    def _get_news_from_database(self, limit: int = 20, offset: int = 0, category: Optional[str] = None) -> Tuple[List[NewsArticle], int]:
        """Get news articles from database (fallback method)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Base query
        base_query = "FROM news_articles"
        where_clause = ""
        params = []
        
        if category and category != "TRANG CH�":
            where_clause = " WHERE category = ?"
            params.append(category)
        
        # Get total count
        count_query = f"SELECT COUNT(*) {base_query} {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get articles with pagination
        articles_query = f"""
            SELECT id, title, source, time, views, thumbnail, category 
            {base_query} {where_clause}
            ORDER BY id DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(articles_query, params)
        
        articles = []
        for row in cursor.fetchall():
            articles.append(NewsArticle(
                id=row[0],
                title=row[1],
                source=row[2],
                time=row[3],
                views=row[4],
                thumbnail=row[5],
                category=row[6]
            ))
        
        conn.close()
        return articles, total

    def get_news_by_id(self, news_id: int) -> Optional[NewsArticle]:
        """Get a single news article by ID"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, source, time, views, thumbnail, category
            FROM news_articles
            WHERE id = ?
        """, (news_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return NewsArticle(
                id=row[0],
                title=row[1],
                source=row[2],
                time=row[3],
                views=row[4],
                thumbnail=row[5],
                category=row[6]
            )
        return None

    def create_news(self, url: str, url_img: str, title: str, description: str, content: str, metadata: dict) -> NewsArticle:
        """Create a new news article"""
        # For now, just return a new NewsArticle object with a generated ID
        # In a real implementation, you might want to save to database
        return NewsArticle(
            id=random.randint(1000, 9999),
            url=url,
            url_img=url_img,
            title=title,
            description=description,
            content=content,
            metadata=metadata
        )

    def update_news(self, news_id: int, url: Optional[str] = None, url_img: Optional[str] = None, 
                   title: Optional[str] = None, description: Optional[str] = None, 
                   content: Optional[str] = None, metadata: Optional[dict] = None) -> Optional[NewsArticle]:
        """Update an existing news article"""
        # For now, just return a new NewsArticle object with updated data
        # In a real implementation, you might want to update database
        return NewsArticle(
            id=news_id,
            url=url or "https://example.com",
            url_img=url_img or "https://example.com/image.jpg",
            title=title or "Updated Article",
            description=description or "Updated description",
            content=content or "Updated content",
            metadata=metadata or {}
        )

    def delete_news(self, news_id: int) -> bool:
        """Delete a news article"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM news_articles WHERE id = ?", (news_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0

    def get_categories(self) -> List[str]:
        """Get all available news categories"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM news_articles ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_random_news_from_json(self, limit: int = 10, category: Optional[str] = None) -> Tuple[List[NewsArticle], int]:
        """Get random news articles from JSON data using pick_random_items function"""
        try:
            # Load config file
            with open("config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load JSON data
            json_path = config["DATA"]["PROCESSED_DATA_IMG_URL"]
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter by category if provided
            def filter_fn(item):
                if not category:
                    return True
                cat = item.get('metadata', {}).get('cat', '').lower()
                return cat == category.lower()
            
            # Get random items using pick_random_items
            random_items = pick_random_items(data, n=limit, filter_fn=filter_fn)
            
            # Convert to new NewsArticle format
            articles = []
            for i, item in enumerate(random_items):
                try:
                    article = NewsArticle(
                        id=1000 + i,
                        url=item.get('url', ''),
                        url_img=item.get('url_img', ''),
                        title=item.get('title', ''),
                        description=item.get('description', ''),
                        content=item.get('content', ''),
                        metadata=item.get('metadata', {})
                    )
                    articles.append(article)
                except Exception as e:
                    print(f"Error converting article {i}: {e}")
                    continue
            
            return articles, len(articles)
            
        except Exception as e:
            print(f"Error getting random news from JSON: {e}")
            # Fallback to empty list since old format doesn't match
            return [], 0
    
    def get_random_articles_raw(self, limit: int = 10, category: Optional[str] = None, 
                               seed: Optional[int] = None) -> List[RandomArticle]:
        """Get random articles in their original format from JSON"""
        try:
            return self.random_service.get_random_articles_from_json(
                n=limit, 
                category=category, 
                seed=seed
            )
        except Exception as e:
            print(f"Error getting raw random articles: {e}")
            return []
    
    def get_json_categories(self) -> List[str]:
        """Get available categories from JSON data"""
        try:
            return self.random_service.get_available_categories()
        except Exception as e:
            print(f"Error getting JSON categories: {e}")
            return self.get_categories()
    
    def get_random_news_json_format(self, limit: int = 10, category: Optional[str] = None, seed: Optional[int] = None):
        """Get random news articles from processed_data_dash.json using pick_random_items, return in original JSON format"""
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                    'data', 'processed_data', 'processed_data_dash.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Optionally filter by category
            def filter_fn(item):
                if not category:
                    return True
                # category may be in item['metadata']['cat'] or item['category']
                cat = item.get('metadata', {}).get('cat') or item.get('category')
                return cat == category
            items = pick_random_items(data, n=limit, seed=seed, filter_fn=filter_fn)
            return items, len(items)
        except Exception as e:
            print(f"Error in get_random_news_json_format: {e}")
            return [], 0
    
    def _convert_json_to_news_article(self, json_item: dict, article_id: int) -> NewsArticle:
        """Convert JSON format article to NewsArticle format"""
        # Extract metadata
        metadata = json_item.get('metadata', {})
        category = metadata.get('cat', 'MỚI')
        
        # Map categories to display format
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
        
        # Extract source from metadata or URL
        source = metadata.get('author', 'VietnamNet')
        if not source or source == '':
            # Try to extract from URL
            url = json_item.get('url', '')
            if 'vietnamnet' in url:
                source = 'VietnamNet'
            elif 'vnexpress' in url:
                source = 'VnExpress'
            elif 'tuoitre' in url:
                source = 'Tuổi Trẻ'
            else:
                source = 'Tin tức'
        
        # Handle time display
        published_date = metadata.get('published_date', '')
        if published_date and '/' in published_date:
            time_display = 'Vài giờ trước'
        else:
            time_display = published_date or 'Vài giờ trước'
        
        # Generate random views for display
        views_count = random.randint(100, 5000)
        views_display = f"{views_count} lượt xem"
        
        return NewsArticle(
            id=article_id,
            title=json_item.get('title', ''),
            source=source,
            time=time_display,
            views=views_display,
            thumbnail=json_item.get('url_img', ''),
            category=mapped_category
        )