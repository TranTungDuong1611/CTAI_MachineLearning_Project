# CTAI Machine Learning Project

## Objective

A comprehensive news aggregation and text analysis system that leverages advanced machine learning techniques to process Vietnamese news articles. The system focuses on three core AI-powered tasks:

1. **News Classification** - Automatically categorizes news articles into predefined topics (politics, economy, sports, health, etc.) using a stacking ensemble model that combines multiple machine learning algorithms for high accuracy classification.

2. **News Summarization** - Generates concise, meaningful summaries of lengthy news articles using a fine-tuned ViT5 transformer model specifically optimized for Vietnamese text, enabling users to quickly grasp key information.

3. **News Clustering** - Groups news articles with similar topics together using advanced sentence transformers and clustering algorithms, helping discover trending stories and related content without predefined categories.

The system features intelligent Vietnamese news crawling from major sources, real-time processing pipelines, and a modern MVC-based FastAPI backend for seamless integration and scalability.

## Key Features

- **Multi-Source News Crawling**: Automated scraping from major Vietnamese news websites (DanTri, VNExpress, VietnamNet)
- **Text Classification**: Stacking ensemble model for accurate news categorization
- **Text Clustering**: Intelligent news grouping using sentence transformers and multiple clustering algorithms
- **Text Summarization**: Fine-tuned ViT5 model for Vietnamese text summarization
- **RESTful API**: FastAPI backend with MVC architecture for seamless integration
- **Real-time Processing**: Efficient text preprocessing and feature engineering pipeline

## Project Structure

```
CTAI_MachineLearning_Project/
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
├── data/                           # Data storage and management
│   ├── raw_data
│   ├── processed_data
│   ├── stop_words
├── docs/                           # Project documentation
├── results/                        # Analysis reports and figures
├── src/                            # Source code modules
│   ├── crawl_data/                 # Web scraping modules
│   │   ├── README.md               # Crawler documentation
│   │   ├── crawl_dantri.py         # DanTri news crawler
│   │   ├── crawl_vnexpress.py      # VNExpress news crawler
│   │   └── crawl_vietnamnet.py     # VietnamNet news crawler
│   ├── data/                       # Data processing utilities
│   │   ├── merge_data.py           # Data merging functions
│   │   └── text_pre_processing.py  # Text preprocessing pipeline
│   ├── models/.                    # Machine learning models
│   │   ├── Text_Classification/    # Classification models
│   │   │   ├── train.py            # Training script
│   │   │   ├── inference.py        # Prediction interface
│   │   │   └── text_data.py        # Data handling
│   │   ├── Text_Clustering/        # Clustering algorithms
│   │   │   └── Text_cluster.py     # Clustering implementation
│   │   └── Text_summarization/     # Summarization models
│   │       ├── finetune_vit.py     # ViT5 fine-tuning
│   │       └── infer.py            # Summarization inference
│   ├── backend/                    # FastAPI backend
│   │   ├── ApplicationBackend.py   # Main FastAPI application
│   │   ├── controller/             # API controllers (MVC)
│   │   │   ├── NewsController.py
│   │   │   ├── ClassificationController.py
│   │   │   ├── ClusteringController.py
│   │   │   └── SummationController.py
│   │   └── service/                # Business logic services
│   │       ├── NewService.py
│   │       ├── ClassificationService.py
│   │       ├── ClusteringService.py
│   │       ├── SummationService.py
│   │       ├── OpenAIService.py
│   │       └── RandomTextService.py
│   ├── frontend/                    # Frontend application
│   └── utils/                       # Utility functions
│       └── RandomText.py
└── LICENSE
```

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome browser (for Selenium crawlers)
- ChromeDriver
- CUDA-compatible GPU (optional, for faster training)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TranTungDuong1611/CTAI_MachineLearning_Project.git
cd CTAI_MachineLearning_Project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install additional packages for web crawling**
```bash
pip install requests beautifulsoup4 selenium
```

### Running the Application

1. **Start the FastAPI backend**
```bash
cd src/backend
python ApplicationBackend.py
```

2. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Interactive API: http://localhost:8000/redoc

## Data Crawling

The project includes sophisticated web crawlers for three major Vietnamese news sources:

### Supported News Sources

| Source | Technology | Categories Covered |
|--------|------------|-------------------|
| **DanTri** | Requests + BeautifulSoup | Xã hội, Kinh doanh, Đời sống, Sức khỏe, Pháp luật, Thế giới, Khoa học, Thể thao, Giải trí, Du lịch, Giáo dục |
| **VNExpress** | Selenium WebDriver | Thời sự, Góc nhìn, Kinh doanh, Đời sống, Pháp luật, Sức khỏe, Thế giới, KHCN, Thể thao, Giải trí, Du lịch, Giáo dục |
| **VietnamNet** | Selenium WebDriver | Chính trị, Thời sự, Kinh doanh, Văn hóa - Giải trí, Sức khỏe, Pháp luật, Thế giới, Công nghệ, Thể thao, Du lịch, Giáo dục |

### Crawler Features

- **Automatic Category Discovery**: Dynamically detects news categories
- **Pagination Support**: Efficiently crawls multiple pages
- **Content Extraction**: Extracts title, description, content, metadata, and images
- **Error Handling**: Robust retry mechanisms and failure recovery
- **Rate Limiting**: Configurable delays to respect website policies
- **JSON Export**: Structured data output for downstream processing

### Usage Example

```python
from src.crawl_data.crawl_dantri import DanTriCrawler

# Initialize crawler
crawler = DanTriCrawler()

# Crawl with custom settings
crawler.run_crawl(
    per_article_delay=0.15,
    max_pages_root=10,
    out_json="data/raw_data/dantri_articles.json"
)
```

## Machine Learning Models

### 1. Text Classification

**Stacking Ensemble Model** for Vietnamese news categorization

- **Base Models**:
  - Linear SVM (C=1.0, squared hinge loss)
  - Logistic Regression (C=1.0, max_iter=1000)
  - Random Forest (n_estimators=302, with sparse-to-dense conversion)
- **Meta Learner**: Linear SVM (C=1.5, squared hinge loss)
- **Cross-Validation**: 6-fold CV for stacking
- **Features**: Combined TF-IDF and statistical features

**Performance Metrics**:
- Training Accuracy: 95%+
- Test Accuracy: 88%+
- F1-Score (Macro): 0.85+
- F1-Score (Weighted): 0.89+

**Training**:
```bash
cd src/models/Text_Classification
python train.py --features path/to/features --results path/to/results --cv 6
```

### 2. Text Clustering

**Multi-Algorithm Clustering** with sentence transformers

- **Embedding Model**: `intfloat/multilingual-e5-large-instruct`
- **Algorithms**:
  - K-Means (optimal K via silhouette score)
  - HDBSCAN (density-based clustering)
  - Agglomerative Clustering (hierarchical)
- **Optimization**: Automatic optimal cluster number detection (range: 8-20)
- **Metrics**: Silhouette score, MSE within clusters

**Key Features**:
- Lazy loading for efficient memory usage
- Cosine similarity-based clustering
- Cluster sampling with centroid proximity
- Vietnamese text preprocessing

### 3. Text Summarization

**Fine-tuned ViT5 Model** for Vietnamese text summarization

- **Base Model**: `VietAI/vit5-large-vietnews-summarization`
- **Architecture**: Sequence-to-Sequence Transformer
- **Training Configuration**:
  - Learning Rate: 5e-5
  - Batch Size: 2 (with gradient accumulation)
  - Max Source Length: 512 tokens
  - Max Target Length: 128 tokens
  - Epochs: 3 with linear warmup

**Features**:
- ROUGE-2 F1 evaluation
- Beam search generation (num_beams=4)
- Automatic mixed precision (FP16)
- Early stopping with best model selection

## Backend Architecture

### MVC Design Pattern

The FastAPI backend follows a clean **Model-View-Controller** architecture:

```
backend/
├── ApplicationBackend.py          # Main FastAPI app with CORS and lifespan management
├── controller/                    # Request handlers (Controllers)
│   ├── NewsController.py          # News CRUD operations
│   ├── ClassificationController.py # Text classification endpoints
│   ├── ClusteringController.py    # Clustering analysis endpoints
│   └── SummationController.py     # Text summarization endpoints
└── service/                       # Business logic (Services/Models)
    ├── NewService.py              # News data management
    ├── ClassificationService.py   # ML classification logic
    ├── ClusteringService.py       # Clustering algorithms
    ├── SummationService.py        # Summarization processing
    ├── OpenAIService.py           # External AI integration
    └── RandomTextService.py       # Utility text generation
```

### API Endpoints

#### News Management
- `GET /api/news` - Retrieve news articles with pagination
- `GET /api/news/{id}` - Get specific article by ID
- `POST /api/news` - Create new article
- `PUT /api/news/{id}` - Update existing article
- `DELETE /api/news/{id}` - Remove article
- `GET /api/news/categories` - List available categories

#### ML Services
- `POST /api/classify` - Classify text into categories
- `POST /api/cluster` - Perform text clustering analysis
- `POST /api/summarize` - Generate text summaries

### Key Features

- **Async/Await**: Full asynchronous request handling
- **CORS Support**: Cross-origin requests for frontend integration
- **Auto Documentation**: Swagger UI and ReDoc integration
- **Error Handling**: Comprehensive HTTP exception handling
- **Data Validation**: Pydantic models for request/response validation
- **Health Checks**: Service status monitoring
- **Startup Events**: Async initialization of ML models

## Development Workflow

### 1. Data Pipeline

```bash
# 1. Crawl news data
python src/crawl_data/crawl_dantri.py

# 2. Preprocess and merge data
python src/data/text_pre_processing.py
python src/data/merge_data.py

# 3. Train models
python src/models/Text_Classification/train.py
python src/models/Text_Clustering/Text_cluster.py
python src/models/Text_summarization/finetune_vit.py
```

### 2. Backend Development

```bash
# Start development server
cd src/backend
uvicorn ApplicationBackend:app --reload --host 0.0.0.0 --port 8000

# Run with production settings
python ApplicationBackend.py
```

## Performance & Metrics

### Model Performance

| Model | Accuracy | F1-Score | Processing Speed |
|-------|----------|----------|------------------|
| Text Classification | 88%+ | 0.85+ | ~50ms per text |
| Text Clustering | Silhouette: 0.7+ | MSE: <0.3 | ~100ms per batch |
| Text Summarization | ROUGE-2: 0.45+ | BLEU: 0.35+ | ~200ms per text |

## Configuration

### Environment Variables

Create an `openai.env` file for external AI services:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Model Paths

Update model paths in respective configuration files:
- Classification: `results/models/Text_Classification/`
- Clustering: Memory-based (no persistent storage)
- Summarization: `src/models/Text_summarization/vit5_finetuned/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
