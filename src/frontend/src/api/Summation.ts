import axios from 'axios';
import { API_URL } from '../config.ts';

// Summarization types and interfaces
export interface SummarizationRequest {
  text: string;
  in_max_len?: number;
  out_max_len?: number;
  beams?: number;
  nrng?: number;
  sample?: boolean;
  temp?: number;
}

export interface SummarizationResponse {
  text: string;
  summary: string;
  parameters?: {
    in_max_len: number;
    out_max_len: number;
    beams: number;
    nrng: number;
    do_sample: boolean;
    temperature: number;
  };
}

export interface ModelInfo {
  model_type: string;
  description: string;
  status: string;
  default_parameters: {
    in_max_len: number;
    out_max_len: number;
    beams: number;
    nrng: number;
    do_sample: boolean;
    temperature: number;
  };
}

export interface ModelInfoResponse {
  model_info: ModelInfo;
}

// Summarize a single text
export const summarizeText = async (
  text: string,
  options: Omit<SummarizationRequest, 'text'> = {}
): Promise<SummarizationResponse> => {
  try {
    const response = await axios.post<SummarizationResponse>(
      `${API_URL}/api/summarization`,
      {
        text,
        in_max_len: options.in_max_len || 512,
        out_max_len: options.out_max_len || 128,
        beams: options.beams || 2,
        nrng: options.nrng || 3,
        sample: options.sample || false,
        temp: options.temp || 1.0
      },
      {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to summarize text'
      );
    }
    throw error;
  }
};

// Legacy endpoint for compatibility (similar to Flask API)
export const summarizeTextLegacy = async (
  text: string,
  options: Omit<SummarizationRequest, 'text'> = {}
): Promise<{ text: string; summary: string }> => {
  try {
    const response = await axios.post<{ text: string; summary: string }>(
      `${API_URL}/summarize`,
      {
        text,
        in_max_len: options.in_max_len || 512,
        out_max_len: options.out_max_len || 128,
        beams: options.beams || 2,
        nrng: options.nrng || 3,
        sample: options.sample || false,
        temp: options.temp || 1.0
      },
      {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to summarize text'
      );
    }
    throw error;
  }
};

// Get summarization model information
export const getSummarizationModelInfo = async (): Promise<ModelInfo> => {
  try {
    const response = await axios.get<ModelInfoResponse>(
      `${API_URL}/api/summarization/info`,
      {
        timeout: 10000,
      }
    );
    return response.data.model_info;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to get model info'
      );
    }
    throw error;
  }
};

// Utility function to format summary result
export const formatSummaryResult = (result: SummarizationResponse): string => {
  return result.summary || 'Không thÃ tóm t¯t vn b£n';
};

// Utility function to get default parameters
export const getDefaultSummarizationParams = () => ({
  in_max_len: 512,
  out_max_len: 128,
  beams: 2,
  nrng: 3,
  sample: false,
  temp: 1.0
});