import axios from 'axios';
import { API_URL } from '../config.ts';

// Clustering types and interfaces
export interface ClusterInfo {
  cluster_id: number;
  cluster_name: string;
  article_count: number;
  keywords: string[];
}

export interface ClusteredArticle {
  id: number;
  url: string;
  url_img: string;
  title: string;
  description: string;
  content: string;
  metadata: Record<string, any>;
  cluster_id: number;
  cluster_name: string;
}

export interface ArticleCluster {
  cluster_info: ClusterInfo;
  articles: ClusteredArticle[];
}

export interface ClustersResponse {
  clusters: ArticleCluster[];
  total_clusters: number;
}

export interface ClusterResponse {
  cluster: ArticleCluster;
}

export interface ClusterInfoResponse {
  clusters: ClusterInfo[];
}

export interface ModelInfo {
  model_type: string;
  description: string;
  status: string;
  available_clusters: number;
}

export interface ModelInfoResponse {
  model_info: ModelInfo;
}

// Get articles grouped by clusters
export const getClustersArticles = async (
  limitPerCluster: number = 5,
  maxClusters: number = 6
): Promise<ClustersResponse> => {
  try {
    const response = await axios.get<ClustersResponse>(
      `${API_URL}/api/clusters`,
      {
        params: {
          limit_per_cluster: limitPerCluster,
          max_clusters: maxClusters
        },
        timeout: 30000,
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to get clustered articles'
      );
    }
    throw error;
  }
};


// Utility functions
export const getRelativeTimeString = (publishedDate?: string): string => {
  if (!publishedDate) return 'Vài giờ trước';
  
  // If it's already a relative time string, return it
  if (publishedDate.includes('giờ') || publishedDate.includes('phút')) {
    return publishedDate;
  }
  
  // Otherwise return a generic time
  return 'Vài giờ trước';
};

export const getSourceFromUrl = (url: string): string => {
  if (url.includes('vietnamnet')) return 'VietnamNet';
  if (url.includes('vnexpress')) return 'VnExpress';
  if (url.includes('tuoitre')) return 'Tuổi Trẻ';
  if (url.includes('thanhnien')) return 'Thanh Niên';
  if (url.includes('dantri')) return 'Dân trí';
  if (url.includes('vov')) return 'VOV';
  if (url.includes('zing')) return 'Zing';
  return 'Tin tức';
};

export const formatViews = (min: number = 100, max: number = 5000): string => {
  const views = Math.floor(Math.random() * (max - min + 1)) + min;
  return `${views} lượt xem`;
};