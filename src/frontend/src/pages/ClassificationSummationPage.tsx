import React, { useState } from "react";
import Footer from "../components/Footer";
import Header from "../components/Header";

const ClassificationSummationPage: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");

  const handleClassify = () => {
    const categories = ["NÓNG", "MỚI", "THỂ THAO"];
    const randomCategory = categories[Math.floor(Math.random() * categories.length)];
    setOutputText(`Phân loại: ${randomCategory}`);
  };

  const handleSummarize = () => {
    setOutputText(
      inputText
        ? `Tóm tắt: ${inputText.substring(0, 50)}...`
        : "Vui lòng nhập văn bản để tóm tắt."
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header Section */}
      <Header />

      {/* Input Section */}
      <section className="w-full flex justify-center py-10 flex-grow">
        <div className="w-1/2 bg-white p-8 rounded-3xl shadow-xl relative overflow-hidden">
          <h2 className="text-2xl font-semibold text-gray-800 mb-5 text-center">
            Nhập nội dung tin tức
          </h2>

          <textarea
            className="w-full p-4 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-teal-400 resize-none mb-5 text-gray-800 text-base"
            rows={6}  // chiều cao textbox
            placeholder="Nhập nội dung tin tức tại đây..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          ></textarea>

          {/* Buttons nằm ngang */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={handleClassify}
              className="flex-1 bg-gradient-to-r from-teal-400 to-teal-500 text-white font-semibold py-3 rounded-2xl shadow-lg hover:scale-105 transform transition-all duration-300"
            >
              Phân loại
            </button>
            <button
              onClick={handleSummarize}
              className="flex-1 bg-gradient-to-r from-teal-400 to-teal-500 text-white font-semibold py-3 rounded-2xl shadow-lg hover:scale-105 transform transition-all duration-300"
            >
              Tóm tắt
            </button>
          </div>

          {outputText && (
            <div
              className="p-5 bg-teal-50 border-l-4 border-teal-400 rounded-2xl animate-fadeIn"
            >
              <p className="text-gray-800 text-base whitespace-pre-line">
                {outputText}
              </p>
            </div>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );


};

export default ClassificationSummationPage;