import sys
import os
sys.path.append(os.getcwd())

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from service.SummationService import SummationService

# Create router for summarization endpoints
summarization_router = APIRouter()

# Request models
class SummarizationRequest(BaseModel):
    text: str
    in_max_len: Optional[int] = 512
    out_max_len: Optional[int] = 128
    beams: Optional[int] = 2
    nrng: Optional[int] = 3
    sample: Optional[bool] = False
    temp: Optional[float] = 1.0

class SummarizationBatchRequest(BaseModel):
    texts: List[str]
    in_max_len: Optional[int] = 512
    out_max_len: Optional[int] = 128
    beams: Optional[int] = 2
    nrng: Optional[int] = 3
    sample: Optional[bool] = False
    temp: Optional[float] = 1.0

# Response models
class SummarizationResponse(BaseModel):
    text: str
    summary: str
    parameters: Dict[str, Any]

class SummarizationBatchResponse(BaseModel):
    results: List[Dict[str, Any]]

class ModelInfoResponse(BaseModel):
    model_info: Dict[str, Any]

# Initialize service
summarization_service = SummationService()

# API Routes
@summarization_router.post("/api/summarization", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    """
    Summarize a single text
    
    Parameters:
    - text: The text to summarize
    - in_max_len: Maximum input length (default: 512)
    - out_max_len: Maximum output length (default: 128)
    - beams: Number of beams for beam search (default: 2)
    - nrng: No repeat ngram size (default: 3)
    - sample: Whether to use sampling (default: False)
    - temp: Temperature for sampling (default: 1.0)
    
    Returns:
    - Summarization result with original text, summary, and parameters
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = summarization_service.summarize_text(
            text=request.text,
            in_max_len=request.in_max_len,
            out_max_len=request.out_max_len,
            beams=request.beams,
            nrng=request.nrng,
            do_sample=request.sample,
            temp=request.temp
        )
        
        return SummarizationResponse(
            text=result["text"],
            summary=result["summary"],
            parameters=result["parameters"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@summarization_router.post("/api/summarization/batch", response_model=SummarizationBatchResponse)
async def summarize_texts_batch(request: SummarizationBatchRequest):
    """
    Summarize multiple texts
    
    Parameters:
    - texts: List of texts to summarize
    - Other parameters: Same as single summarization
    
    Returns:
    - List of summarization results
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        if len(request.texts) > 50:  # Limit batch size for summarization
            raise HTTPException(status_code=400, detail="Maximum 50 texts per batch")
        
        results = summarization_service.summarize_texts(
            texts=request.texts,
            in_max_len=request.in_max_len,
            out_max_len=request.out_max_len,
            beams=request.beams,
            nrng=request.nrng,
            do_sample=request.sample,
            temp=request.temp
        )
        
        return SummarizationBatchResponse(results=results)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@summarization_router.get("/api/summarization/info", response_model=ModelInfoResponse)
async def get_summarization_model_info():
    """
    Get information about the summarization model
    
    Returns:
    - Model information and default parameters
    """
    try:
        model_info = summarization_service.get_model_info()
        return ModelInfoResponse(model_info=model_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

# Legacy endpoint for compatibility with existing Flask API
@summarization_router.post("/summarize", response_model=Dict[str, Any])
async def summarize_text_legacy(request: SummarizationRequest):
    """
    Legacy endpoint for summarization (Flask API compatibility)
    
    Parameters:
    - text: The text to summarize
    - in_max_len, out_max_len, beams, nrng, sample, temp: Optional parameters
    
    Returns:
    - Summarization result (direct format for compatibility)
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Missing 'text' in JSON body")
        
        result = summarization_service.summarize_text(
            text=request.text,
            in_max_len=request.in_max_len,
            out_max_len=request.out_max_len,
            beams=request.beams,
            nrng=request.nrng,
            do_sample=request.sample,
            temp=request.temp
        )
        
        # Return in original Flask API format
        return {
            "text": result["text"],
            "summary": result["summary"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")