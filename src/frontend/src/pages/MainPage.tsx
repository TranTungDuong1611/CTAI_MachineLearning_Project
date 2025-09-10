import React, { useState, useEffect } from "react";
import { getNews, getRandomNews } from '../api/MainPage';

interface NewsArticle {
  id: number;
  url: string;
  url_img: string;
  title: string;
  description: string;
  content: string;
  metadata: Record<string, any>;
}

interface NewsCardProps {
  article: NewsArticle;
}

const NewsCard: React.FC<NewsCardProps> = ({ article }) => {
  // Extract source from metadata or URL
  const source = article.metadata?.author || 
    (article.url.includes('vietnamnet') ? 'VietnamNet' : 
     article.url.includes('vnexpress') ? 'VnExpress' : 
     article.url.includes('tuoitre') ? 'Tuổi Trẻ' : 'Tin tức');
     
  // Extract time from metadata
  const time = article.metadata?.published_date || 'Vài giờ trước';
  
  // Generate view count
  const views = `${Math.floor(Math.random() * 5000) + 100} lượt xem`;
  
  const handleClick = () => {
    if (article.url) {
      window.open(article.url, '_blank');
    }
  };

  return (
    <div className="flex bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden cursor-pointer" onClick={handleClick}>
      {/* Ảnh cố định bên trái */}
      <div className="flex-shrink-0">
        <img
          src={article.url_img}
          alt={article.title}
          className="w-[128px] h-[96px] object-cover rounded-md"
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/128x96?text=No+Image';
          }}
        />
      </div>

      {/* Nội dung bên phải */}
      <div className="flex flex-col justify-between flex-1 p-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900 mb-2 leading-snug hover:text-teal-600">
            {article.title}
          </h3>
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
            {article.description}
          </p>
        </div>
        <div className="flex items-center text-xs text-gray-500 space-x-3">
          <span className="text-red-500 font-medium">{source}</span>
          <span>{time}</span>
          <span className="flex items-center">
            <i className="fas fa-eye mr-1"></i>
            {views}
          </span>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
            {article.metadata?.cat || 'Tin tức'}
          </span>
        </div>
      </div>
    </div>
  );
};

const NewsWebsite: React.FC = () => {
  const [activeTab] = useState("TRANG CHỦ");
  const [newsData, setNewsData] = useState<NewsArticle[]>([]);
  const [filteredNews, setFilteredNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNewsData = async (isRandom: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      const response = isRandom ? await getRandomNews(12) : await getNews();
      const fetchedNews = response.data as NewsArticle[];
      setNewsData(fetchedNews);
      
      if (activeTab === "TRANG CHỦ") {
        setFilteredNews(fetchedNews);
      } else {
        setFilteredNews(fetchedNews.filter((news: NewsArticle) => news.metadata?.cat === activeTab));
      }
    } catch (err) {
      setError('Không thể tải dữ liệu tin tức. Vui lòng thử lại sau.');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNewsData();
  }, []);

  useEffect(() => {
    if (activeTab === "TRANG CHỦ") {
      setFilteredNews(newsData);
    } else {
      setFilteredNews(newsData.filter((news) => news.metadata?.cat === activeTab));
    }
  }, [activeTab, newsData]);

  if (loading) {
    return (
      <div className="flex flex-col bg-white">
        <main className="flex-grow max-w-6xl mx-auto px-4 py-6">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Đang tải tin tức...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col bg-white">
        <main className="flex-grow max-w-6xl mx-auto px-4 py-6">
          <div className="text-center py-12">
            <div className="text-red-500 text-6xl mb-4">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={() => fetchNewsData()}   // gọi mà không truyền tham số
              className="bg-teal-500 text-white px-6 py-2 rounded-lg hover:bg-teal-600 transition-colors duration-200"
            >
              Thử lại
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col bg-white">
      {/* Main Content */}
      <main className="flex-grow max-w-6xl mx-auto px-4 py-6">
        {filteredNews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Không có tin tức nào để hiển thị.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-6">
              {filteredNews.map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>

            {/* Action Buttons */}
            <div className="text-center mt-8 space-x-4">
              <button 
                onClick={() => fetchNewsData(false)}
                className="bg-teal-500 text-white px-6 py-2 rounded-lg hover:bg-teal-600 transition-colors duration-200 inline-flex items-center shadow-md"
              >
                <span>Làm mới tin tức</span>
                <i className="fas fa-sync-alt ml-2"></i>
              </button>
              <button 
                onClick={() => fetchNewsData(true)}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors duration-200 inline-flex items-center shadow-md"
              >
                <span>Tin tức ngẫu nhiên</span>
                <i className="fas fa-random ml-2"></i>
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default NewsWebsite;
