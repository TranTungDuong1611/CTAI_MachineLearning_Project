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

interface NavigationTabProps {
  label: string;
  isActive?: boolean;
  onClick: () => void;
  isHashTag?: boolean;
}

const NavigationTab: React.FC<NavigationTabProps> = ({
  label,
  isActive,
  onClick,
  isHashTag = false,
}) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium text-sm transition-colors duration-200 ${
        isHashTag
          ? "bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          : isActive
          ? "text-white bg-teal-500 border-b-2 border-teal-500"
          : "text-gray-700 hover:text-teal-500 hover:border-b-2 hover:border-teal-300"
      }`}
    >
      {isHashTag ? `# ${label}` : label}
    </button>
  );
};

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
  const [activeTab, setActiveTab] = useState("NÓNG");
  const [filteredNews, setFilteredNews] = useState<NewsArticle[]>(newsData);

  const mainTabs = ["NÓNG", "MỚI", "VIDEO", "CHỦ ĐỀ"];
  const hashTags = ["Năng lượng tích cực", "Nghị quyết 57", "Khám phá Việt Nam"];

  useEffect(() => {
    if (activeTab === "NÓNG") {
      setFilteredNews(newsData);
    } else {
      setFilteredNews(newsData.filter((news) => news.category === activeTab));
    }
  }, [activeTab]);

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4">
          {/* Navigation Tabs */}
          <div className="flex items-center space-x-1 py-3 border-b">
            {mainTabs.map((tab) => (
              <NavigationTab
                key={tab}
                label={tab}
                isActive={activeTab === tab}
                onClick={() => setActiveTab(tab)}
              />
            ))}
            <div className="flex-1"></div>
            <div className="flex items-center space-x-2">
              {hashTags.map((tag) => (
                <NavigationTab
                  key={tag}
                  label={tag}
                  isHashTag={true}
                  onClick={() => console.log(`Clicked ${tag}`)}
                />
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-2 gap-6">
          {filteredNews.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))}
        </div>

        {/* Load More Button */}
        <div className="text-center mt-8">
          <button className="bg-teal-500 text-white px-6 py-2 rounded-lg hover:bg-teal-600 transition-colors duration-200 flex items-center mx-auto">
            <span>Xem thêm tin tức</span>
            <i className="fas fa-arrow-down ml-2"></i>
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
          <div className="max-w-6xl mx-auto px-4">
              <div className="grid grid-cols-4 gap-8">
                  <div>
                      <h3 className="text-lg font-semibold mb-4">Về chúng tôi</h3>
                      <p className="text-gray-300 text-sm">
                          Website tin tức hàng đầu Việt Nam, cập nhật thông tin nhanh chóng và chính xác.
                      </p>
                  </div>
                  <div>
                      <h3 className="text-lg font-semibold mb-4">Chuyên mục</h3>
                      <ul className="space-y-2 text-sm text-gray-300">
                          <li><a href="#" className="hover:text-white">Thời sự</a></li>
                          <li><a href="#" className="hover:text-white">Thể thao</a></li>
                          <li><a href="#" className="hover:text-white">Kinh tế</a></li>
                          <li><a href="#" className="hover:text-white">Giải trí</a></li>
                      </ul>
                  </div>
                  <div>
                      <h3 className="text-lg font-semibold mb-4">Liên hệ</h3>
                      <div className="text-sm text-gray-300 space-y-2">
                          <p><i className="fas fa-phone mr-2"></i>1900 123 456</p>
                          <p><i className="fas fa-envelope mr-2"></i>info@news.vn</p>
                          <p><i className="fas fa-map-marker-alt mr-2"></i>Hà Nội, Việt Nam</p>
                      </div>
                  </div>
                  <div>
                      <h3 className="text-lg font-semibold mb-4">Theo dõi chúng tôi</h3>
                      <div className="flex space-x-4">
                          <a href="#" className="text-gray-300 hover:text-white text-xl">
                              <i className="fab fa-facebook"></i>
                          </a>
                          <a href="#" className="text-gray-300 hover:text-white text-xl">
                              <i className="fab fa-twitter"></i>
                          </a>
                          <a href="#" className="text-gray-300 hover:text-white text-xl">
                              <i className="fab fa-youtube"></i>
                          </a>
                          <a href="#" className="text-gray-300 hover:text-white text-xl">
                              <i className="fab fa-instagram"></i>
                          </a>
                      </div>
                  </div>
              </div>
              <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
                  <p>&copy; 2024 Vietnamese News Website. Tất cả quyền được bảo lưu.</p>
              </div>
          </div>
      </footer>
    </div>
  );
};

export default NewsWebsite;
