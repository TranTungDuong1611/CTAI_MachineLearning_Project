import os
import sys
from typing import Dict, Any

# Add path to access models  
sys.path.append(os.getcwd())

try:
    from src.models.Text_Classification import inference as classification
except ImportError as e:
    print(f"Warning: Could not import classification model: {e}")
    classification = None

class ClassificationService:
    """Service for text classification operations"""
    
    def __init__(self):
        """Initialize the classification service"""
        pass
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify a single text
        
        Args:
            text (str): The text to classify
            
        Returns:
            Dict[str, Any]: Classification result
            
        Raises:
            ValueError: If text is empty or None
            Exception: If classification fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or None")
        
        if classification is None:
            raise Exception("Classification model is not available. Please check model installation.")
        
        try:
            result = classification.predict_one(text)
            return result
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")
    
    def classify_texts(self, texts: list) -> list:
        """
        Classify multiple texts
        
        Args:
            texts (list): List of texts to classify
            
        Returns:
            list: List of classification results
            
        Raises:
            ValueError: If texts list is empty
            Exception: If classification fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        results = []
        for text in texts:
            try:
                result = self.classify_text(text)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the classification model
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "model_type": "text_classification",
            "description": "Text classification model for Vietnamese news",
            "status": "active"
        }