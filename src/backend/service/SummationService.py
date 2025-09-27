import os
import sys
from typing import Dict, Any, Optional

# Add path to access models
HERE = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(HERE, "../../"))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

try:
    from models.Text_summarization import infer as summarization
except ImportError as e:
    print(f"Warning: Could not import summarization model: {e}")
    summarization = None

class SummationService:
    """Service for text summarization operations"""
    
    def __init__(self):
        """Initialize the summarization service"""
        pass
    
    def summarize_text(
        self,
        text: str,
        in_max_len: int = 512,
        out_max_len: int = 128,
        beams: int = 2,
        nrng: int = 3,
        do_sample: bool = False,
        temp: float = 1.0
    ) -> Dict[str, Any]:
        """
        Summarize a single text
        
        Args:
            text (str): The text to summarize
            in_max_len (int): Maximum input length
            out_max_len (int): Maximum output length
            beams (int): Number of beams for beam search
            nrng (int): No repeat ngram size
            do_sample (bool): Whether to use sampling
            temp (float): Temperature for sampling
            
        Returns:
            Dict[str, Any]: Summarization result containing original text and summary
            
        Raises:
            ValueError: If text is empty or None
            Exception: If summarization fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or None")
        
        # Validate parameters
        in_max_len = max(1, min(in_max_len, 2048))  # Reasonable limits
        out_max_len = max(1, min(out_max_len, 512))
        beams = max(1, min(beams, 10))
        nrng = max(1, min(nrng, 5))
        temp = max(0.1, min(temp, 2.0))
        
        try:
            if summarization is None:
                # Fallback mock summarization
                summary = self._mock_summarize(text, out_max_len)
            else:
                summary = summarization.summarize_one(
                    text,
                    in_max_len=in_max_len,
                    out_max_len=out_max_len,
                    num_beams=beams,
                    no_repeat_ngram_size=nrng,
                    do_sample=do_sample,
                    temperature=temp,
                )
            
            return {
                "text": text,
                "summary": summary,
                "parameters": {
                    "in_max_len": in_max_len,
                    "out_max_len": out_max_len,
                    "beams": beams,
                    "nrng": nrng,
                    "do_sample": do_sample,
                    "temperature": temp
                }
            }
        except Exception as e:
            raise Exception(f"Summarization failed: {str(e)}")
    
    def _mock_summarize(self, text: str, max_len: int) -> str:
        """Mock summarization for when the model is not available"""
        sentences = text.split('.')
        if len(sentences) <= 1:
            return text[:max_len] + "..." if len(text) > max_len else text
        
        # Take first few sentences up to max_len
        summary = ""
        for sentence in sentences:
            if len(summary + sentence + ".") <= max_len:
                summary += sentence + "."
            else:
                break
        
        return summary if summary else text[:max_len] + "..."
    
    def summarize_texts(
        self,
        texts: list,
        in_max_len: int = 512,
        out_max_len: int = 128,
        beams: int = 2,
        nrng: int = 3,
        do_sample: bool = False,
        temp: float = 1.0
    ) -> list:
        """
        Summarize multiple texts
        
        Args:
            texts (list): List of texts to summarize
            Other parameters: Same as summarize_text
            
        Returns:
            list: List of summarization results
            
        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        results = []
        for text in texts:
            try:
                result = self.summarize_text(
                    text=text,
                    in_max_len=in_max_len,
                    out_max_len=out_max_len,
                    beams=beams,
                    nrng=nrng,
                    do_sample=do_sample,
                    temp=temp
                )
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "text": text})
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the summarization model
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "model_type": "text_summarization",
            "description": "Text summarization model for Vietnamese news",
            "status": "active" if summarization is not None else "mock",
            "default_parameters": {
                "in_max_len": 512,
                "out_max_len": 128,
                "beams": 2,
                "nrng": 3,
                "do_sample": False,
                "temperature": 1.0
            }
        }