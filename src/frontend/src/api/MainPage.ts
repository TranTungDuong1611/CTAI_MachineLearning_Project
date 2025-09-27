import axios from 'axios';
import { API_URL } from '../config.ts';

// Lấy danh sách tất cả news
export const getNews = async () => {
  return axios.get(`${API_URL}/api/news`);
};

// Lấy danh sách news ngẫu nhiên với số lượng giới hạn
export const getRandomNews = async (limit: number = 10) => {
  return axios.get(`${API_URL}/api/news?limit=${limit}`);
};

// Lấy chi tiết 1 news theo id
export const getNewsById = async (id: number) => {
  return axios.get(`${API_URL}/api/news/${id}`);
};

// Tạo mới một news
export const createNews = async (newsData: {
  url: string;
  url_img: string;
  title: string;
  description: string;
  content: string;
  metadata: Record<string, any>;
}) => {
  return axios.post(`${API_URL}/api/news`, newsData, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

// Cập nhật 1 news theo id
export const updateNews = async (id: number, newsData: {
  url?: string;
  url_img?: string;
  title?: string;
  description?: string;
  content?: string;
  metadata?: Record<string, any>;
}) => {
  return axios.put(`${API_URL}/api/news/${id}`, newsData, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

// Xóa 1 news theo id
export const deleteNews = async (id: number) => {
  return axios.delete(`${API_URL}/api/news/${id}`);
};
