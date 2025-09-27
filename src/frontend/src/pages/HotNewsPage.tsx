import React, { useState, useEffect } from 'react';
import { getClustersArticles, getSourceFromUrl, getRelativeTimeString } from '../api/Clustering';
import type { ArticleCluster, ClusteredArticle } from '../api/Clustering';

interface ArticleCardProps {
  article: ClusteredArticle;
  isLarge?: boolean;
}

const ArticleCard: React.FC<ArticleCardProps> = ({ article, isLarge = false }) => {
  const source = getSourceFromUrl(article.url);
  const timeString = getRelativeTimeString(article.metadata?.published_date);

  const handleClick = () => {
    if (article.url) {
      window.open(article.url, '_blank');
    }
  };

  if (isLarge) {
    return (
        <div
            className="group cursor-pointer hover:bg-gray-50 transition-colors duration-200"
            onClick={handleClick}
        >
        <div className="flex gap-3 p-4 items-start h-[120px]">
        {/* Image */}
        <div className="flex-shrink-0">
            <div className="relative">
            <img
                src={article.url_img}
                alt={article.title}
                className="w-[120px] h-[96px] object-cover rounded-lg shadow-sm"
                onError={(e) => {
                (e.target as HTMLImageElement).src =
                    "https://via.placeholder.com/120x96?text=📰&bg=f3f4f6";
                }}
            />
            </div>
        </div>

        {/* Text */}
        <div className="flex-1 min-w-0 flex flex-col justify-between">
            <h3 className="font-semibold text-gray-900 text-sm leading-snug mb-1 overflow-hidden text-ellipsis"
                style={{
                display: "-webkit-box",
                WebkitBoxOrient: "vertical",
                WebkitLineClamp: 2,
                overflow: "hidden"
                }}>
            {article.title}
            </h3>
            <div className="flex items-center gap-3 text-xs">
            <span className="text-red-500 font-medium">{source}</span>
            <span className="text-gray-500">{timeString}</span>
            </div>
        </div>
        </div>
    </div>
    );
  }

  return (
    <div 
      className="group cursor-pointer hover:bg-gray-50 transition-colors duration-200"
      onClick={handleClick}
    >
      <div className="flex gap-3 p-3 border-b border-gray-100 last:border-b-0">
        <div className="flex-shrink-0">
          <img 
            src={article.url_img} 
            alt={article.title}
            className="w-30 h-24 object-cover rounded shadow-sm"
            style={{ width: '120px', height: '96px' }}
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/120x96?text=📰&bg=f3f4f6';
            }}
          />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-gray-900 line-clamp-2 mb-1 group-hover:text-blue-600 transition-colors leading-tight">
            {article.title}
          </h4>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-red-500 font-medium">{source}</span>
            <span className="text-gray-500">{timeString}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

interface ClusterSectionProps {
  cluster: ArticleCluster;
}

const ClusterSection: React.FC<ClusterSectionProps> = ({ cluster }) => {
  const mainArticle = cluster.articles[0];
  const otherArticles = cluster.articles.slice(1, 4); // Limit to 3 additional articles

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Section Header */}
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 px-4 py-2.5">
        <div className="flex items-center justify-between">
          <h2 className="text-white font-bold text-base flex items-center gap-2">
            <span className="text-lg">#</span>
            {cluster.cluster_info.cluster_name.toUpperCase()}
          </h2>
        </div>
      </div>

      {/* Articles Container */}
      <div>
        {/* Main Article */}
        {mainArticle && (
          <div className="border-b-2 border-gray-100">
            <ArticleCard article={mainArticle} isLarge={true} />
          </div>
        )}
        
        {/* Secondary Articles */}
        {otherArticles.length > 0 && (
          <div>
            {otherArticles.map((article, index) => (
              <ArticleCard key={`${article.id}-${index}`} article={article} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const LoadingSkeleton: React.FC = () => (
  <div className="min-h-screen bg-gray-50">
    <div className="max-w-full mx-auto px-4 py-6">
      {/* Header skeleton */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 bg-gray-300 rounded animate-pulse"></div>
          <div className="h-8 bg-gray-300 rounded w-48 animate-pulse"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-96 animate-pulse"></div>
      </div>
      
      {/* Grid skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border overflow-hidden">
            {/* Header skeleton */}
            <div className="h-12 bg-gray-300 animate-pulse"></div>
            
            {/* Main article skeleton */}
            <div className="p-4 border-b-2 border-gray-100">
              <div className="flex gap-3">
                <div className="w-24 h-16 bg-gray-300 rounded-lg animate-pulse" style={{ width: '96px', height: '64px' }}></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded w-4/5 animate-pulse"></div>
                  <div className="h-3 bg-gray-100 rounded w-1/2 animate-pulse"></div>
                </div>
              </div>
            </div>
            
            {/* Secondary articles skeleton */}
            {[...Array(3)].map((_, j) => (
              <div key={j} className="p-3 border-b border-gray-100 last:border-b-0">
                <div className="flex gap-3">
                  <div className="w-16 h-12 bg-gray-200 rounded animate-pulse" style={{ width: '64px', height: '48px' }}></div>
                  <div className="flex-1 space-y-1">
                    <div className="h-3 bg-gray-200 rounded animate-pulse"></div>
                    <div className="h-3 bg-gray-200 rounded w-4/5 animate-pulse"></div>
                    <div className="h-2 bg-gray-100 rounded w-1/3 animate-pulse"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ErrorState: React.FC<{ error: string; onRetry: () => void }> = ({ error, onRetry }) => (
  <div className="min-h-screen bg-gray-50">
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center py-20">
        <div className="text-red-500 text-6xl mb-6">⚠️</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Có lỗi xảy ra</h2>
        <p className="text-red-600 mb-8 text-lg max-w-md mx-auto">{error}</p>
        <button 
          onClick={onRetry}
          className="bg-teal-500 text-white px-8 py-3 rounded-lg hover:bg-teal-600 transition-colors shadow-md font-medium inline-flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Thử lại
        </button>
      </div>
    </div>
  </div>
);

const EmptyState: React.FC<{ onRefresh: () => void }> = ({ onRefresh }) => (
  <div className="text-center py-20">
    <div className="text-6xl mb-6">📰</div>
    <h2 className="text-2xl font-bold text-gray-900 mb-4">
      Không có tin nổi bật
    </h2>
    <p className="text-gray-600 text-lg mb-8 max-w-md mx-auto">
      Hiện tại không có tin nổi bật nào để hiển thị. Vui lòng thử lại sau.
    </p>
    <button 
      onClick={onRefresh}
      className="bg-teal-500 text-white px-8 py-3 rounded-lg hover:bg-teal-600 transition-colors shadow-md font-medium inline-flex items-center gap-2"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      Làm mới
    </button>
  </div>
);

const HotNewsPage: React.FC = () => {
  const [clusters, setClusters] = useState<ArticleCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);
  const [useSampleClusters, setUseSampleClusters] = useState(true);

  const fetchHotNews = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');
      
      let response = await getClustersArticles(4, 6); // 4 articles per cluster, 6 clusters max
      
      setClusters(response.clusters);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Có lỗi xảy ra khi tải tin hot';
      setError(errorMessage);
      console.error('Error fetching hot news:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHotNews();
  }, []);

  useEffect(() => {
    fetchHotNews();
  }, [useSampleClusters]);


  const handleRefresh = () => {
    fetchHotNews(true);
  };

  if (loading && !refreshing) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={() => fetchHotNews()} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Header Section */}
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <h1 className="text-3xl font-bold text-gray-900">
              CHỦ ĐỀ
            </h1>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-lg mb-3">
                Cập nhật những tin tức được quan tâm nhiều nhất, phân nhóm theo chủ đề
              </p>
            </div>
            <button 
              onClick={handleRefresh}
              disabled={refreshing}
              className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-600 transition-colors shadow-sm font-medium inline-flex items-center gap-2 text-sm disabled:opacity-50"
            >
              <svg 
                className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {refreshing ? 'Đang tải...' : 'Làm mới'}
            </button>
          </div>
        </header>

        {/* News Grid */}
        {clusters.length > 0 ? (
          <>
            <div className="grid grid-cols-2 gap-6 mb-12">
              {clusters.map((cluster) => (
                <ClusterSection key={cluster.cluster_info.cluster_id} cluster={cluster} />
              ))}
            </div>

            {/* Bottom Actions */}
            <footer className="text-center">
              <button 
                onClick={handleRefresh}
                disabled={refreshing}
                className="bg-teal-500 text-white px-8 py-3 rounded-lg hover:bg-teal-600 transition-colors inline-flex items-center shadow-md font-medium disabled:opacity-50"
              >
                {refreshing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Đang cập nhật...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Cập nhật tin mới
                  </>
                )}
              </button>
            </footer>
          </>
        ) : (
          <EmptyState onRefresh={handleRefresh} />
        )}
      </div>
    </div>
  );
};

export default HotNewsPage;
