import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Footer from "./components/Footer";
import NewWebsite from "./pages/MainPage.tsx";
import ClassificationSummationPage from "./pages/ClassificationSummationPage.tsx";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-grow">{children}</main>
      <Footer />
    </div>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<NewWebsite />} />
          <Route path="/classify-summarize" element={<ClassificationSummationPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
