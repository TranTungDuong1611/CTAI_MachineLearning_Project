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
    <div className="flex flex-col min-h-screen bg-white">
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
    </div>
  );
};

export default NewsWebsite;
