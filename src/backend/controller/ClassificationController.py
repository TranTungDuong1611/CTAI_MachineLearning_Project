from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
# Add service path
sys.path.append(os.getcwd())

from src.backend.service.ClassificationService import ClassificationService

# Create router for classification endpoints
classification_router = APIRouter()

# Request models
class ClassificationRequest(BaseModel):
    text: str

class ClassificationBatchRequest(BaseModel):
    texts: List[str]

# Response models
class ClassificationResponse(BaseModel):
    result: Dict[str, Any]

class ClassificationBatchResponse(BaseModel):
    results: List[Dict[str, Any]]

class ModelInfoResponse(BaseModel):
    model_info: Dict[str, Any]

# Initialize service
classification_service = ClassificationService()

# API Routes
@classification_router.post("/api/classification", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    """
    Classify a single text
    
    Parameters:
    - text: The text to classify
    
    Returns:
    - Classification result
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = classification_service.classify_text(request.text)
        return ClassificationResponse(result=result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@classification_router.post("/api/classification/batch", response_model=ClassificationBatchResponse)
async def classify_texts_batch(request: ClassificationBatchRequest):
    """
    Classify multiple texts
    
    Parameters:
    - texts: List of texts to classify
    
    Returns:
    - List of classification results
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        if len(request.texts) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
        
        results = classification_service.classify_texts(request.texts)
        return ClassificationBatchResponse(results=results)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@classification_router.get("/api/classification/info", response_model=ModelInfoResponse)
async def get_classification_model_info():
    """
    Get information about the classification model
    
    Returns:
    - Model information
    """
    try:
        model_info = classification_service.get_model_info()
        return ModelInfoResponse(model_info=model_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

# Legacy endpoint for compatibility with existing Flask API
@classification_router.post("/classification", response_model=Dict[str, Any])
async def classify_text_legacy(request: ClassificationRequest):
    """
    Legacy endpoint for classification (Flask API compatibility)
    
    Parameters:
    - text: The text to classify
    
    Returns:
    - Classification result (direct format for compatibility)
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Missing 'text' in JSON body")
        
        result = classification_service.classify_text(request.text)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")