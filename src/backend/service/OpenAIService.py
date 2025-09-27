import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

class OpenAIService:
    """Service for OpenAI API operations"""
    
    def __init__(self):
        """Initialize OpenAI service with API key"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key from various sources"""
        api_key = None
        
        # Try to get API key from openai.env file
        try:
            env_file_path = os.path.join(os.getcwd(), "openai.env")
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    content = f.read().strip()
                    if content and '=' in content:
                        api_key = content.split('=', 1)[1].strip()
                    elif content:
                        api_key = content
        except Exception as e:
            print(f"Warning: Could not read openai.env: {e}")
        
        # Fallback to environment variable
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize client if API key is available
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
        else:
            print("Warning: No OpenAI API key found. OpenAI features will be disabled.")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.client is not None
    
    def generate_cluster_label(self, articles: List[Dict[str, Any]], max_words: int = 5) -> str:
        """
        Generate a cluster label based on article titles and content
        
        Args:
            articles: List of articles with title, description, and content
            max_words: Maximum number of words for the label (default: 5)
            
        Returns:
            str: Generated cluster label
        """
        if not self.is_available():
            return self._generate_fallback_label(articles, max_words)
        
        try:
            # Prepare article texts for analysis
            article_texts = []
            for article in articles[:5]:  # Use maximum 5 articles for analysis
                title = article.get('title', '')
                description = article.get('description', '')
                # Combine title and description (limit length to avoid token limits)
                text = f"{title}. {description}"
                if text.strip():
                    article_texts.append(text)
            
            if not article_texts:
                return self._generate_fallback_label(articles, max_words)
            
            # Create prompt for cluster label generation
            prompt = f"""Analyze these Vietnamese news article titles and descriptions to generate a topic label.

                    Articles:
                    {chr(10).join([f"- {text}" for text in article_texts])}

                    Generate a concise topic label in Vietnamese that captures the main theme of these articles.
                    Requirements:
                    - Maximum {max_words} words
                    - In Vietnamese language
                    - Represent the common theme/topic
                    - Use clear, descriptive terms
                    - Return only the label, no explanation

                    Label:"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a Vietnamese news categorization expert. Generate concise, accurate topic labels for news clusters."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.0
            )
            
            # Extract and clean the response
            label = response.choices[0].message.content.strip()
            
            # Clean up the label (remove quotes, extra spaces, etc.)
            label = label.strip('"\'').strip()
            
            # Ensure word limit
            words = label.split()
            if len(words) > max_words:
                label = ' '.join(words[:max_words])
            
            return label.upper() if label else self._generate_fallback_label(articles, max_words)
            
        except Exception as e:
            print(f"Error generating cluster label with OpenAI: {e}")
            return self._generate_fallback_label(articles, max_words)
    
    def _generate_fallback_label(self, articles: List[Dict[str, Any]], max_words: int = 5) -> str:
        """
        Generate a fallback label when OpenAI is not available
        
        Args:
            articles: List of articles
            max_words: Maximum number of words for the label
            
        Returns:
            str: Fallback cluster label
        """
        if not articles:
            return "TIN TỨC"
        
        # Simple keyword extraction from titles
        common_keywords = [
            ("chính trị", "CHÍNH TRỊ"),
            ("kinh tế", "KINH TẾ"), 
            ("thể thao", "THỂ THAO"),
            ("giáo dục", "GIÁO DỤC"),
            ("y tế", "Y TẾ"),
            ("công nghệ", "CÔNG NGHỆ"),
            ("xã hội", "XÃ HỘI"),
            ("pháp luật", "PHÁP LUẬT"),
            ("quốc tế", "QUỐC TẾ"),
            ("địa phương", "ĐỊA PHƯƠNG"),
            ("văn hóa", "VĂN HÓA"),
            ("du lịch", "DU LỊCH"),
            ("môi trường", "MÔI TRƯỜNG"),
            ("giao thông", "GIAO THÔNG"),
            ("nepal", "NEPAL"),
            ("ba lan", "BA LAN"),
            ("nato", "NATO"),
            ("đại học", "GIÁO DỤC"),
            ("bắt giữ", "PHÁP LUẬT"),
            ("cảnh sát", "AN NINH"),
            ("công an", "AN NINH")
        ]
        
        # Combine all article texts
        all_text = ""
        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            all_text += f" {title} {description}"
        
        # Find matching keywords
        for keyword, label in common_keywords:
            if keyword in all_text:
                return label
        
        # If no keywords found, use a generic label
        return "TIN NỔI BẬT"
    
    def generate_multiple_labels(self, clusters_data: List[Dict[str, Any]], max_words: int = 5) -> Dict[int, str]:
        """
        Generate labels for multiple clusters
        
        Args:
            clusters_data: List of cluster data with articles
            max_words: Maximum number of words per label
            
        Returns:
            Dict[int, str]: Mapping of cluster_id to generated label
        """
        labels = {}
        
        for cluster_data in clusters_data:
            cluster_id = cluster_data.get('cluster_id', 0)
            articles = cluster_data.get('articles', [])
            
            label = self.generate_cluster_label(articles, max_words)
            labels[cluster_id] = label
        
        return labels