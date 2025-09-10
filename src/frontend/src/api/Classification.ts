import axios from 'axios';
import { API_URL } from '../config.ts';

// Classification request and response types
export interface ClassificationRequest {
  text: string;
}

export interface ClassificationResult {
  category?: string;
  confidence?: number;
  label?: string;
  score?: number;
  [key: string]: any; // Allow additional properties from the model
}

export interface ClassificationResponse {
  result: ClassificationResult;
}

export interface ClassificationBatchRequest {
  texts: string[];
}

export interface ClassificationBatchResponse {
  results: ClassificationResult[];
}

export interface ModelInfo {
  model_type: string;
  description: string;
  status: string;
}

export interface ModelInfoResponse {
  model_info: ModelInfo;
}

// Classify a single text using the new API endpoint
export const classifyText = async (text: string): Promise<ClassificationResult> => {
  try {
    const response = await axios.post<ClassificationResponse>(
      `${API_URL}/api/classification`,
      { text },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 second timeout
      }
    );
    return response.data.result;
  } catch (error) {
    throw error;
  }
};

// Classify multiple texts in batch
export const classifyTextsBatch = async (texts: string[]): Promise<ClassificationResult[]> => {
  try {
    const response = await axios.post<ClassificationBatchResponse>(
      `${API_URL}/api/classification/batch`,
      { texts },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 60000, // 60 second timeout for batch
      }
    );
    return response.data.results;
  } catch (error) {
    throw error;
  }
};

// Get model information
export const getClassificationModelInfo = async (): Promise<ModelInfo> => {
  try {
    const response = await axios.get<ModelInfoResponse>(
      `${API_URL}/api/classification/info`,
      {
        timeout: 10000, // 10 second timeout
      }
    );
    return response.data.model_info;
  } catch (error) {
    throw error;
  }
};

// Legacy API endpoint for backward compatibility
export const classifyTextLegacy = async (text: string): Promise<ClassificationResult> => {
  try {
    const response = await axios.post<ClassificationResult>(
      `${API_URL}/classification`,
      { text },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000,
      }
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Utility function to format classification result for display
export const formatClassificationResult = (result: ClassificationResult): string => {
  if (result.category) {
    return result.category;
  }
  if (result.pred_label) {
    return result.pred_label;
  }
  // If the result has other properties, try to extract the main classification
  const keys = Object.keys(result);
  if (keys.length > 0) {
    return String(result[keys[0]]);
  }
  return 'Unknown';
};

// Utility function to get confidence score
export const getConfidenceScore = (result: ClassificationResult): number => {
  return result.confidence || result.score || 0;
};