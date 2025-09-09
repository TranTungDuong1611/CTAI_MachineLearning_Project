import React, { useState, useEffect } from "react";

// Mock news data
interface NewsArticle {
  id: number;
  title: string;
  source: string;
  time: string;
  views: string;
  thumbnail: string;
  category: string;
}

const newsData: NewsArticle[] = [
  {
    id: 1,
    title: "Thủ tướng Campuchia gửi lời tới tân Thủ tướng Thái Lan",
    source: "TTXVN",
    time: "2 giờ",
    views: "1013 lượt xem",
    thumbnail:
      "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "NÓNG",
  },
  {
    id: 2,
    title:
      "Giá vàng khó bứt phá mạnh như trước, không nên mua đuổi theo thị trường",
    source: "VietNamNet",
    time: "3 giờ",
    views: "3152 lượt xem",
    thumbnail: "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "NÓNG",
  },
  {
    id: 3,
    title: "Điều ông Trump lo lắng nhất",
    source: "ZNEWS",
    time: "3 giờ",
    views: "1233 lượt xem",
    thumbnail: "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "MỚI",
  },
  {
    id: 4,
    title:
      "Bắt Mạnh 'Gô' - triệt xóa tận gốc băng nhóm Vi 'Ngố' ở Thanh Hóa",
    source: "Công an nhân dân",
    time: "22 phút",
    views: "142 lượt xem",
    thumbnail: "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "NÓNG",
  },
  {
    id: 5,
    title:
      "Vòng loại U23 châu Á: Tuyển Việt Nam quyết thắng Yemen để đi tiếp với ngôi đầu",
    source: "VietnamPlus",
    time: "27 phút",
    views: "203 lượt xem",
    thumbnail:
      "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "THỂ THAO",
  },
  {
    id: 6,
    title: "Tuyển Anh tỉnh mộng trước 'tí hon' Andorra",
    source: "Người Lao Động",
    time: "1 giờ",
    views: "1 lượt xem",
    thumbnail:
      "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2024/8/23/su-hoi-sinh-cua-chang-ca-si-tre-tung-chim-sau-trong-giac-ngu-dong-suot-3-nam-428.jpg?width=0&s=AUzDKXWvoXd4dqET0AYRvw",
    category: "THỂ THAO",
  },
];

interface NewsCardProps {
  article: NewsArticle;
}

const NewsCard: React.FC<NewsCardProps> = ({ article }) => {
  return (
    <div className="flex bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* Ảnh cố định bên trái */}
      <div className="flex-shrink-0">
        <img
          src={article.thumbnail}
          alt={article.title}
          className="w-[128px] h-[96px] object-cover rounded-md"
        />
      </div>

      {/* Nội dung bên phải */}
      <div className="flex flex-col justify-between flex-1 p-4">
        <h3 className="text-base font-semibold text-gray-900 mb-2 leading-snug hover:text-teal-600 cursor-pointer">
          {article.title}
        </h3>
        <div className="flex items-center text-xs text-gray-500 space-x-3">
          <span className="text-red-500 font-medium">{article.source}</span>
          <span>{article.time}</span>
          <span className="flex items-center">
            <i className="fas fa-eye mr-1"></i>
            {article.views}
          </span>
        </div>
      </div>
    </div>
  );
};

const NewsWebsite: React.FC = () => {
  const [activeTab] = useState("TRANG CHỦ");
  const [filteredNews, setFilteredNews] = useState<NewsArticle[]>(newsData);

  useEffect(() => {
    if (activeTab === "TRANG CHỦ") {
      setFilteredNews(newsData);
    } else {
      setFilteredNews(newsData.filter((news) => news.category === activeTab));
    }
  }, [activeTab]);

  return (
    <div className="flex flex-col bg-white">
      {/* Main Content */}
      <main className="flex-grow max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-2 gap-6">
          {filteredNews.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))}
        </div>

        {/* Load More Button */}
        <div className="text-center mt-8">
          <button className="bg-teal-500 text-white px-6 py-2 rounded-lg hover:bg-teal-600 transition-colors duration-200 flex items-center mx-auto shadow-md">
            <span>Xem thêm tin tức</span>
            <i className="fas fa-arrow-down ml-2"></i>
          </button>
        </div>
      </main>
    </div>
  );
};

export default NewsWebsite;
