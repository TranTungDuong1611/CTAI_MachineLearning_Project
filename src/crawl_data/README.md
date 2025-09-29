# Web Crawlers for Vietnamese News Sites

This directory contains refactored web crawlers for three major Vietnamese news websites:

- **DanTri** (`crawl_dantri.py`) - Uses requests and BeautifulSoup
- **VNExpress** (`crawl_vnexpress.py`) - Uses Selenium WebDriver
- **VietnamNet** (`crawl_vietnamnet.py`) - Uses Selenium WebDriver

## Features

All crawlers provide the following functionality:

1. **Category Discovery**: Automatically discover news categories from the homepage
2. **URL Collection**: Collect article URLs from category pages with pagination support
3. **Content Extraction**: Extract article title, description, content, metadata, and images
4. **Data Export**: Save results as JSON files organized by category
5. **Error Handling**: Robust error handling with retry mechanisms
6. **Image Support**: Extract and save article thumbnail images

## Requirements

### For DanTri Crawler
```bash
pip install requests beautifulsoup4
```

### For VNExpress and VietnamNet Crawlers
```bash
pip install selenium
```

Note: You'll also need Chrome browser and ChromeDriver installed for Selenium-based crawlers.

## Usage

### DanTri Crawler

```python
from crawl_dantri import DanTriCrawler

# Create crawler instance
crawler = DanTriCrawler()

# Run crawling with custom settings
crawler.run_crawl(
    per_article_delay=0.15,      # Delay between articles (seconds)
    max_pages_root=10,           # Max pages per category
    out_json="data/raw_data/dantri_articles.json"  # Output file
)
```

### VNExpress Crawler

```python
from crawl_vnexpress import VNExpressCrawler

# Create crawler instance (headless=True for background operation)
crawler = VNExpressCrawler(headless=True)

# Crawl all categories
crawler.crawl_all_categories(
    num_articles_per_cat=200,    # Articles per category
    output_dir="data/raw_data/vnexpress"  # Output directory
)
```

### VietnamNet Crawler

```python
from crawl_vietnamnet import VietNamNetCrawler

# Create crawler instance
crawler = VietNamNetCrawler(headless=True)

# Crawl all categories
crawler.crawl_all_categories(
    num_articles_per_cat=200,    # Articles per category
    output_dir="data/raw_data/vietnamnet" # Output directory
)
```

## Output Format

All crawlers generate JSON files with the following structure:

```json
{
  "url": "https://example.com/article.html",
  "title": "Article Title",
  "description": "Article description/summary",
  "content": "Full article content",
  "url_img": "https://example.com/image.jpg",
  "metadata": {
    "cat": "Main Category",
    "subcat": "Sub Category",
    "published_date": "2023-01-01",
    "author": "Author Name"
  }
}
```

## Configuration

### Categories

Each crawler targets specific news categories:

**DanTri**: Xã hội, Kinh doanh, Đời sống, Sức khỏe, Pháp luật, Thế giới, Khoa học, Thể thao, Giải trí, Du lịch, Giáo dục

**VNExpress**: Thời sự, Góc nhìn, Kinh doanh, Đời sống, Pháp luật, Sức khỏe, Thế giới, KHCN, Thể thao, Giải trí, Du lịch, Giáo dục

**VietnamNet**: Chính trị, Thời sự, Kinh doanh, Văn hóa - Giải trí, Sức khỏe, Pháp luật, Thế giới, Công nghệ, Thể thao, Du lịch, Giáo dục

### Chrome Options (Selenium Crawlers)

Both Selenium crawlers use optimized Chrome options:
- Headless mode for background operation
- Disabled GPU, extensions, and dev-shm-usage
- No sandbox mode for compatibility

## Advanced Usage

### Custom Category Selection

```python
# For VietnamNet crawler
crawler = VietNamNetCrawler()
crawler.TARGET_CATS = ["Thời sự", "Kinh doanh"]  # Crawl only specific categories
crawler.crawl_all_categories()
```

### Individual Operations

```python
# Get categories only
categories = crawler.get_categories()

# Crawl URLs for specific category
urls = crawler.crawl_category_urls("https://example.com/category", num_articles=50)

# Extract content from specific URL
content = crawler.extract_article_content("https://example.com/article.html")
```

## Error Handling

All crawlers include comprehensive error handling:

- Network timeouts and retries
- Missing HTML elements
- Stale element references (Selenium)
- Page load failures
- Invalid URLs

Failed articles are logged but don't stop the crawling process.

## Performance Tips

1. **Rate Limiting**: Use appropriate delays between requests to avoid being blocked
2. **Headless Mode**: Use headless=True for faster Selenium operations
3. **Batch Processing**: Process articles in batches to manage memory usage
4. **Resume Support**: Save URLs first, then extract content to allow resuming

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: Ensure ChromeDriver is in PATH or install via package manager
2. **Element not found**: Website structure may have changed - check selectors
3. **Timeout errors**: Increase timeout values or check network connection
4. **Memory issues**: Reduce num_articles_per_cat or add periodic cleanup

### Debugging

Enable verbose logging by catching and printing exceptions:

```python
try:
    crawler.crawl_all_categories()
except Exception as e:
    print(f"Crawling failed: {e}")
    import traceback
    traceback.print_exc()
```