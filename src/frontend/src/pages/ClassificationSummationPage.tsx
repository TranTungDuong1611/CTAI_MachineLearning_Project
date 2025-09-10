import React, { useState } from "react";
import { classifyText, formatClassificationResult, getConfidenceScore } from '../api/Classification';

const ClassificationSummationPage: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [category, setCategory] = useState("");
  const [isClassifying, setIsClassifying] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [error, setError] = useState("");
  const [confidence, setConfidence] = useState<number>(0);

  const handleClassify = async () => {
    if (!inputText.trim()) {
      setError("Vui lòng nhập văn bản để phân loại");
      return;
    }

    setIsClassifying(true);
    setError("");
    setCategory("");
    setOutputText("");

    try {
      const result = await classifyText(inputText);
      const classificationResult = formatClassificationResult(result);
      const confidenceScore = getConfidenceScore(result);
      
      setCategory(classificationResult);
      setConfidence(confidenceScore);
      setOutputText(`Phân loại: ${classificationResult}${
        confidenceScore > 0 ? ` (Độ tin cậy: ${(confidenceScore * 100).toFixed(1)}%)` : ''
      }`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Có lỗi xảy ra khi phân loại văn bản';
      setError(errorMessage);
      setOutputText(`Lỗi: ${errorMessage}`);
    } finally {
      setIsClassifying(false);
    }
  };

  const handleSummarize = async () => {
    if (!inputText.trim()) {
      setError("Vui lòng nhập văn bản để tóm tắt");
      return;
    }

    setIsSummarizing(true);
    setError("");
    setCategory("");
    setOutputText("");

    try {
      // For now, use a simple summarization (you can replace this with actual API call)
      const summary = inputText.length > 150 
        ? `${inputText.substring(0, 150)}...`
        : inputText;
      setOutputText(`Tóm tắt: ${summary}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Có lỗi xảy ra khi tóm tắt văn bản';
      setError(errorMessage);
      setOutputText(`Lỗi: ${errorMessage}`);
    } finally {
      setIsSummarizing(false);
    }
  };

  const getCurrentDate = () => {
    return new Date().toLocaleDateString('vi-VN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-gray-100">
      {/* Newspaper Header */}
      <header className="bg-white border-b-4 border-black">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-6xl font-bold font-serif text-black mb-2">
              BÁO TIN TỨC AI
            </h1>
            <div className="flex justify-between items-center text-sm text-gray-600 border-t border-b border-gray-300 py-2 mt-4">
              <span className="font-semibold">{getCurrentDate()}</span>
              <span className="font-semibold">PHÂN LOẠI & TÓM TẮT TIN TỨC</span>
              <span className="font-semibold">SỐ 001</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Input Column */}
          <div className="col-span-5 bg-white border border-gray-300 overflow-hidden">
            <div className="bg-black text-white p-3">
              <h2 className="text-xl font-bold font-serif text-center">
                NHẬP NỘI DUNG TIN TỨC
              </h2>
            </div>
            <div className="p-6">
              <textarea
                className="w-full p-4 border border-gray-400 focus:outline-none focus:border-black resize-none mb-6 text-gray-800 font-serif leading-relaxed box-border"
                rows={12}
                placeholder="Nhập nội dung tin tức tại đây để phân loại và tóm tắt..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
              
              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 text-sm">
                  {error}
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={handleClassify}
                  disabled={isClassifying || isSummarizing || !inputText.trim()}
                  className="bg-black text-white font-bold py-3 px-4 hover:bg-gray-800 transition-colors font-serif disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isClassifying ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      ĐANG PHÂN LOẠI...
                    </>
                  ) : (
                    "PHÂN LOẠI"
                  )}
                </button>
                <button
                  onClick={handleSummarize}
                  disabled={isClassifying || isSummarizing || !inputText.trim()}
                  className="bg-black text-white font-bold py-3 px-4 hover:bg-gray-800 transition-colors font-serif disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isSummarizing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      ĐANG TÓM TẮT...
                    </>
                  ) : (
                    "TÓM TẮT"
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Vertical Divider */}
          <div className="col-span-1 flex justify-center">
            <div className="w-px bg-black"></div>
          </div>

          {/* Output Column */}
          <div className="col-span-6 bg-white border border-gray-300">
            <div className="bg-black text-white p-3">
              <h2 className="text-xl font-bold font-serif text-center">
                KẾT QUẢ PHÂN TÍCH
              </h2>
            </div>
            <div className="p-6">
              {outputText ? (
                <article className="newspaper-article">
                  {category && (
                    <div className="mb-4">
                      <span className="inline-block bg-black text-white px-3 py-1 text-sm font-bold font-serif">
                        CHUYÊN MỤC: {category}
                      </span>
                      {confidence > 0 && (
                        <span className="ml-2 inline-block bg-green-600 text-white px-2 py-1 text-xs font-bold">
                          {(confidence * 100).toFixed(1)}% tin cậy
                        </span>
                      )}
                    </div>
                  )}
                  
                  <h3 className="text-2xl font-bold font-serif mb-4 leading-tight border-b-2 border-black pb-2">
                    {inputText ? inputText.substring(0, 60) + "..." : "Tiêu đề tin tức"}
                  </h3>
                  
                  <div className="text-base leading-relaxed font-serif text-justify">
                    <p className="mb-4 first-letter:text-6xl first-letter:font-bold first-letter:float-left first-letter:mr-2 first-letter:leading-none">
                      {outputText.replace(/^(Tóm tắt: |Phân loại: )/, '')}
                    </p>
                    
                    {inputText && (
                      <div className="mt-6 pt-4 border-t border-gray-300">
                        <p className="text-sm text-gray-600 italic">
                          * Nội dung được phân tích và xử lý bởi hệ thống AI
                        </p>
                        {category && confidence > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            Độ chính xác: {(confidence * 100).toFixed(2)}%
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </article>
              ) : (
                <div className="text-center text-gray-500 py-12">
                  <div className="text-6xl mb-4">📰</div>
                  <p className="text-lg font-serif">
                    Nhập nội dung và nhấn "Phân loại" hoặc "Tóm tắt" <br />
                    để xem kết quả hiển thị như báo
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
        
      </main>
    </div>
  );
};

export default ClassificationSummationPage;