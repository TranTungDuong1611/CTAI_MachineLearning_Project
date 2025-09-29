import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class VNExpressCrawler:
    def __init__(self, headless=True):
        self.MAGAZINE_NAME = "vnexpress"
        self.HOME_PAGE = "https://vnexpress.net/"

        # Target categories for crawling
        self.EXCLUDING_CATEGORIES = [
            "Thời sự", "Góc nhìn", "Kinh doanh", "Đời sống", "Pháp luật",
            "Sức khỏe", "Thế giới", "KHCN", "Thể thao", "Giải trí", "Du lịch", "Giáo dục"
        ]

        # Chrome options
        self.chrome_options = webdriver.ChromeOptions()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.page_load_strategy = "normal"

        self.driver = None

    def init_driver(self):
        """Initialize Chrome driver"""
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def close_driver(self):
        """Close Chrome driver"""
        if self.driver:
            self.driver.close()

    def get_categories(self):
        """Get all available categories from VNExpress homepage"""
        if not self.driver:
            self.init_driver()

        self.driver.get(self.HOME_PAGE)

        # Click menu button
        try:
            all_menu = self.driver.find_element(by=By.CLASS_NAME, value="hamburger")
            all_menu.click()
        except NoSuchElementException:
            print("Could not find menu button")
            return []

        # Get categories
        cats = []
        try:
            sub_menu = self.driver.find_element(by=By.CLASS_NAME, value="row-menu")
            cat_menus = sub_menu.find_elements(by=By.TAG_NAME, value="a")

            for cat_name in cat_menus:
                cat = cat_name.get_attribute("title").strip()
                href = cat_name.get_attribute("href").strip()

                if cat in self.EXCLUDING_CATEGORIES:
                    cats.append({"cat_names": cat, "url": href})
        except NoSuchElementException:
            print("Could not find category menu")

        return cats

    def crawl_category_urls(self, category_url, num_articles=200):
        """Crawl article URLs from a category page"""
        if not self.driver:
            self.init_driver()

        results = []
        crawled_urls = set()
        url = category_url

        print(f"[START] category: {category_url}")

        while len(results) < num_articles and url:
            self.driver.get(url)

            try:
                parent_paper_url = self.driver.find_element(By.CLASS_NAME, "list-news-subfolder")
                list_paper = parent_paper_url.find_elements(By.CLASS_NAME, "item-news-common")
            except NoSuchElementException:
                print(f"[WARN] Không tìm thấy danh sách bài ở: {url}")
                break

            # Skip first 2 items (spotlight articles)
            for paper in list_paper[2:]:
                if len(results) >= num_articles:
                    break
                try:
                    # Get paper URL
                    url_html = paper.find_element(By.TAG_NAME, "a")
                    url_new = url_html.get_attribute("href") or ""

                    # Get avatar URL
                    img_el = paper.find_element(By.CLASS_NAME, "thumb-art").find_element(By.CSS_SELECTOR, "picture img")
                    avatar_paper = img_el.get_attribute("data-src") or img_el.get_attribute("src") or ""

                    if url_new.startswith(self.HOME_PAGE) and url_new not in crawled_urls:
                        crawled_urls.add(url_new)
                        results.append({
                            "paper_url": url_new,
                            "avatar_url": avatar_paper
                        })
                except (StaleElementReferenceException, NoSuchElementException):
                    continue
                except Exception as e:
                    print(f"[SKIP] Lỗi không mong muốn khi xử lý item ở {url}: {e}")
                    continue

            print(f"[PROGRESS] {len(results)}/{num_articles} collected | last page: {url}")

            if len(results) >= num_articles:
                break

            # Find next page
            next_href = None
            try:
                next_pages = self.driver.find_element(By.CLASS_NAME, "next-page")
                next_href = next_pages.get_attribute("href")

                if not next_href:
                    try:
                        next_href = next_pages.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except NoSuchElementException:
                        next_href = None

                if not next_href:
                    try:
                        self.driver.execute_script("arguments[0].click();", next_pages)
                        next_href = self.driver.current_url if self.driver.current_url != url else None
                    except Exception:
                        next_href = None
            except NoSuchElementException:
                next_href = None

            if not next_href or next_href == url:
                print("[INFO] Không tìm thấy trang tiếp theo. Dừng.")
                break

            url = next_href

        print(f"[DONE] Collected {len(results)} items for category {category_url}")
        return results

    def extract_article_content(self, article_url, avatar_url=None):
        """Extract content and metadata from article URL"""
        if not self.driver:
            self.init_driver()

        self.driver.get(article_url)

        try:
            # Title
            title = self.driver.find_element(by=By.CSS_SELECTOR, value="h1.title-detail").text

            # Description
            description = self.driver.find_element(by=By.CLASS_NAME, value="description").text

            # Categories
            lis_cat = []
            sub_cat = self.driver.find_element(by=By.CLASS_NAME, value="breadcrumb")
            lis_cats = sub_cat.find_elements(by=By.TAG_NAME, value="a")
            for cat in lis_cats:
                category = cat.get_attribute("title")
                if len(category):
                    lis_cat.append(category)

            main_cat = lis_cat[0] if lis_cat else "Unknown"
            subb_cat = lis_cat[1] if len(lis_cat) > 1 and lis_cat[1] is not None else None

            # Published date
            published_date = self.driver.find_element(by=By.CLASS_NAME, value="date").text

            # Content
            article = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.fck_detail"))
            )

            paras = [p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "p.Normal") if p.text.strip()]

            contents = []
            author = []

            if paras:
                contents = paras[:-1]
                author = [paras[-1]]

            return {
                "url": article_url,
                "title": title,
                "description": description,
                "content": "\n".join(contents),
                "metadata": {
                    "cat": main_cat,
                    "subcat": subb_cat,
                    "published_date": published_date,
                    "author": author,
                    "avatar_url": avatar_url
                }
            }

        except (NoSuchElementException, Exception) as e:
            print(f"Error extracting content from {article_url}: {e}")
            return None

    def crawl_all_categories(self, num_articles_per_cat=200, output_dir="data/vnexpress"):
        """Crawl all categories and save articles"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Get categories
        categories = self.get_categories()
        print(f"Found {len(categories)} categories")

        # First pass: collect URLs
        all_category_urls = {}
        for cat in categories:
            cat_name = cat['cat_names']
            url = cat['url']
            print(f"Collecting URLs for {cat_name}...")
            urls = self.crawl_category_urls(url, num_articles_per_cat)
            all_category_urls[cat_name] = urls

        # Save URLs
        url_file = os.path.join(output_dir, "vnexpress_urls.json")
        with open(url_file, "w", encoding="utf-8") as f:
            json.dump(all_category_urls, f, ensure_ascii=False, indent=4)

        # Second pass: extract content
        for cat_name, urls in all_category_urls.items():
            print(f"Extracting content for {cat_name}...")
            cat_data = []

            for url_data in urls:
                if isinstance(url_data, dict):
                    article_url = url_data.get("paper_url")
                    avatar_url = url_data.get("avatar_url")
                else:
                    article_url = url_data
                    avatar_url = None

                try:
                    article = self.extract_article_content(article_url, avatar_url)
                    if article:
                        cat_data.append(article)
                except Exception as e:
                    print(f"Error processing {article_url}: {e}")
                    continue

            # Save category data
            name_file_cat = cat_name.lower().replace(" ", "-") + ".json"
            cat_file = os.path.join(output_dir, name_file_cat)
            with open(cat_file, "w", encoding="utf-8") as f:
                json.dump(cat_data, f, ensure_ascii=False, indent=4)

            print(f"Saved {len(cat_data)} articles for {cat_name}")

        self.close_driver()
        print("Crawling completed!")


if __name__ == "__main__":
    crawler = VNExpressCrawler(headless=True)
    crawler.crawl_all_categories(
        num_articles_per_cat=200,
        output_dir="data/raw_data/vnexpress"
    )