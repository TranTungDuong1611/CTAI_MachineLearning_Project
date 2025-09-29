import os
import json
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class VietNamNetCrawler:
    def __init__(self, headless=True):
        self.MAGAZINE_NAME = "vietnamnet"
        self.HOME_PAGE = "https://vietnamnet.vn/"

        # Target categories for crawling
        self.TARGET_CATS = [
            "Chính trị", "Thời sự", "Kinh doanh", "Văn hóa - Giải trí",
            "Sức khỏe", "Pháp luật", "Thế giới", "Công nghệ",
            "Thể thao", "Du lịch", "Giáo dục"
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
        self.crawled_urls = set()
        self.visited_pages = set()

    def init_driver(self):
        """Initialize Chrome driver"""
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def close_driver(self):
        """Close Chrome driver"""
        if self.driver:
            self.driver.close()

    def get_categories(self):
        """Get all available categories from VietNamNet homepage"""
        if not self.driver:
            self.init_driver()

        self.driver.get(self.HOME_PAGE)

        cats = []
        try:
            sub_menu = self.driver.find_element(by=By.CLASS_NAME, value="header_submenu-content-list")
            cat_menus = sub_menu.find_elements(by=By.TAG_NAME, value="a")

            for cat_name in cat_menus:
                cat = cat_name.get_attribute("title").strip()
                href = cat_name.get_attribute("href").strip()

                # Skip premium and specific pages
                if cat == "premium vietnamnet" or cat == "Hành trình Việt Nam":
                    continue
                else:
                    cats.append({"cat_names": cat, "url": href})
        except NoSuchElementException:
            print("Could not find category menu")

        return cats

    def _abs(self, href):
        """Convert relative URL to absolute"""
        return urljoin(self.HOME_PAGE, href) if href else None

    def _first_from_srcset(self, srcset_val):
        """Extract first URL from srcset attribute"""
        if not srcset_val:
            return None
        first_part = srcset_val.split(",")[0].strip()
        return first_part.split()[0] if first_part else None

    def _first_non_empty(self, *vals):
        """Return first non-empty value from arguments"""
        for v in vals:
            if v and v.strip() and not v.strip().startswith("data:image/"):
                return v.strip()
        return None

    def get_avatar_url_by_article_url(self, article_url):
        """Get avatar URL for a specific article URL"""
        try:
            avatar_divs = self.driver.find_elements(by=By.CLASS_NAME, value="verticalPost__avt")

            for avatar_div in avatar_divs:
                try:
                    link_element = avatar_div.find_element(by=By.TAG_NAME, value="a")
                    href = self._abs(link_element.get_attribute("href"))

                    if href and href == article_url:
                        img_element = avatar_div.find_element(by=By.TAG_NAME, value="img")
                        img_url = self._first_non_empty(
                            self._first_from_srcset(img_element.get_attribute("data-srcset")),
                            self._first_from_srcset(img_element.get_attribute("srcset")),
                            img_element.get_attribute("data-src"),
                            img_element.get_attribute("data-original"),
                            img_element.get_attribute("data-lazy"),
                            img_element.get_attribute("src"),
                        )
                        if img_url:
                            print(f"Found avatar for {article_url}: {img_url}")
                            return img_url
                except NoSuchElementException:
                    continue
            return None
        except Exception as e:
            print(f"Error getting avatar for {article_url}: {e}")
            return None

    def _find_next_page_url(self):
        """Find next page URL safely"""
        try:
            pag = self.driver.find_element(by=By.CLASS_NAME, value="pagination__list")
            # Priority: rel="next"
            nxt = pag.find_elements(by=By.CSS_SELECTOR, value='a[rel="next"]')
            if nxt:
                return self._abs(nxt[0].get_attribute("href"))
            # Or active li + next li
            act = pag.find_elements(by=By.CSS_SELECTOR, value="li.active")
            if act:
                sib = act[0].find_elements(by=By.XPATH, value="following-sibling::li[1]/a")
                if sib:
                    return self._abs(sib[0].get_attribute("href"))
            # Fallback: text 'Sau'/'Next'
            for a in pag.find_elements(by=By.TAG_NAME, value="a"):
                if (a.text or "").strip().lower() in {"sau", "next", "›", ">>"}:
                    return self._abs(a.get_attribute("href"))
        except NoSuchElementException:
            pass
        return None

    def fill_missing_images_via_og(self, items):
        """Fill missing image URLs using og:image meta tags"""
        for it in items:
            if it.get("url_img"):
                continue
            try:
                self.driver.get(it["url"])
                metas = self.driver.find_elements(By.CSS_SELECTOR, 'meta[property="og:image"]')
                if metas:
                    it["url_img"] = metas[0].get_attribute("content") or None
                    if it["url_img"]:
                        print(f"Filled og:image for {it['url']}: {it['url_img']}")
            except Exception as e:
                print(f"OG fallback failed for {it['url']}: {e}")
        return items

    def crawl_category_urls(self, category_url, num_articles=200):
        """Crawl article URLs from a category page"""
        if not self.driver:
            self.init_driver()

        all_data = []
        url = category_url

        while (num_articles is None or len(all_data) < num_articles) and url and url not in self.visited_pages:
            self.visited_pages.add(url)
            self.driver.get(url)

            title_news = self.driver.find_elements(by=By.CLASS_NAME, value="vnn-title")

            for title in title_news:
                try:
                    a = title.find_element(by=By.TAG_NAME, value="a")
                    url_new = self._abs(a.get_attribute("href"))
                    if not url_new or not url_new.startswith(self.HOME_PAGE):
                        continue
                    if url_new in self.crawled_urls:
                        continue

                    avatar_url = self.get_avatar_url_by_article_url(url_new)

                    article_data = {
                        "url": url_new,
                        "url_img": avatar_url
                    }
                    all_data.append(article_data)
                    self.crawled_urls.add(url_new)

                    if num_articles and len(all_data) >= num_articles:
                        break

                except (StaleElementReferenceException, NoSuchElementException):
                    continue
                except Exception as e:
                    print(f"Error processing article: {e}")

            if num_articles and len(all_data) >= num_articles:
                break

            # Find next page safely
            next_url = self._find_next_page_url()
            if not next_url or next_url in self.visited_pages:
                print("Cannot find next page or already visited, stopping crawl for this category")
                break
            url = next_url

        # Statistics
        with_img = sum(1 for it in all_data if it.get("url_img"))
        print(f"[{category_url}] collected {len(all_data)} items, {with_img} with images, {len(all_data)-with_img} without.")
        return all_data

    def extract_article_content(self, article_url, url_img=None):
        """Extract content and metadata from article URL"""
        if not self.driver:
            self.init_driver()

        self.driver.get(article_url)

        try:
            # Title & description
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.content-detail-title").text.strip()
            description = self.driver.find_element(By.CLASS_NAME, "sm-sapo-mb-0").text.strip()

            # Categories
            lis_cat = []
            try:
                cats = self.driver.find_element(By.CLASS_NAME, "sm-show-time")
                lis_cats = cats.find_elements(By.TAG_NAME, "li")
                lis_cats = lis_cats[1:]  # Skip first item
                for cat in lis_cats:
                    category = cat.text.strip()
                    if category:
                        lis_cat.append(category)
            except NoSuchElementException:
                pass

            main_cat = lis_cat[0] if lis_cat else "Unknown"
            sub_cat_val = lis_cat[-1] if len(lis_cat) > 1 else "None"

            # Published date
            try:
                published_date = self.driver.find_element(By.CLASS_NAME, "bread-crumb-detail__time").text.strip()
            except NoSuchElementException:
                published_date = ""

            # Content
            contents = []
            author_str = "Unknown"
            article = self.driver.find_element(By.CLASS_NAME, "main-content")
            children = article.find_elements(By.XPATH, "./*")

            for child in children:
                text = child.text.strip()
                if not text:
                    continue

                if child.tag_name.lower() in {"p", "h1", "h2", "h3", "h4"}:
                    contents.append(text)
                elif child.tag_name.lower() == "figure":
                    # Caption (<=100) wrap in [] ; longer considered content
                    if len(text) <= 100:
                        contents.append(f"[{text}]")
                    else:
                        contents.append(text)

            # Author(s)
            authors = []
            try:
                wrapper = self.driver.find_element(By.CLASS_NAME, "article-detail-author-wrapper")
                author_names = wrapper.find_elements(By.CLASS_NAME, "name")
                for a in author_names:
                    # Priority <a title="...">, fallback text
                    t = (a.find_element(By.CSS_SELECTOR, "a").get_attribute("title")
                         if len(a.find_elements(By.CSS_SELECTOR, "a"))
                         else a.text).strip()
                    if t:
                        authors.append(t)
            except NoSuchElementException:
                pass

            if authors:
                author_str = ", ".join(dict.fromkeys(authors))  # unique & stable order
            else:
                # Fallback: try to get last line as author signature
                if contents:
                    last = contents[-1]
                    dash_pos = last.find('-')
                    if 0 <= dash_pos <= 30:
                        # Example: "Nguyễn A - Tổng hợp"
                        possible = last[:dash_pos].strip()
                        if possible:
                            author_str = possible

            return {
                "url": article_url,
                "url_img": url_img,
                "title": title,
                "description": description,
                "content": "\n".join(contents),
                "metadata": {
                    "cat": main_cat,
                    "subcat": sub_cat_val,
                    "published_date": published_date,
                    "author": author_str
                }
            }

        except Exception as e:
            print(f"Error extracting content from {article_url}: {e}")
            return None

    def crawl_all_categories(self, num_articles_per_cat=200, output_dir="data/raw_data/vietnamnet"):
        """Crawl all categories and save articles"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Get categories
        categories = self.get_categories()
        filtered_cats = [c for c in categories if c['cat_names'] in self.TARGET_CATS]
        print(f"Found {len(filtered_cats)} target categories")

        # First pass: collect URLs
        all_category_urls = {}
        for cat in filtered_cats:
            cat_name = cat['cat_names']
            url = cat['url']
            print(f"Collecting URLs for {cat_name}...")
            article_data = self.crawl_category_urls(url, num_articles_per_cat)

            # Fill missing images via og:image
            article_data = self.fill_missing_images_via_og(article_data)
            all_category_urls[cat_name] = article_data

        # Save URLs
        url_file = os.path.join(output_dir, "vietnamnet_urls.json")
        with open(url_file, "w", encoding="utf-8") as f:
            json.dump(all_category_urls, f, ensure_ascii=False, indent=4)

        print(f"Saved {sum(len(v) for v in all_category_urls.values())} articles URLs")

        # Second pass: extract content
        for cat_name, urls in all_category_urls.items():
            print(f"Extracting content for {cat_name}...")
            cat_data = []

            for url_data in urls:
                if isinstance(url_data, dict):
                    article_url = url_data.get("url")
                    url_img = url_data.get("url_img")
                else:
                    article_url = url_data
                    url_img = None

                try:
                    article = self.extract_article_content(article_url, url_img=url_img)
                    if article:
                        cat_data.append(article)
                except Exception as e:
                    print(f"Error processing {article_url}: {e}")
                    continue

            # Save category data
            name_file_cat = cat_name.lower().replace(" ", "-").replace("---", "-") + ".json"
            cat_file = os.path.join(output_dir, name_file_cat)
            with open(cat_file, "w", encoding="utf-8") as f:
                json.dump(cat_data, f, ensure_ascii=False, indent=4)

            print(f"Saved {len(cat_data)} articles for {cat_name}")

        self.close_driver()
        print("Crawling completed!")


if __name__ == "__main__":
    crawler = VietNamNetCrawler(headless=True)
    crawler.crawl_all_categories(
        num_articles_per_cat=200,
        output_dir="data/raw_data/vietnamnet"
    )