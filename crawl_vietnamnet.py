#!/usr/bin/env python
# coding: utf-8

# # Chuẩn bị thư viện

# In[10]:


import os
os.makedirs("data", exist_ok=True)

from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import os
import json


# In[2]:


# selenium setups
## https://www.tutorialspo/int.com/selenium/selenium_webdriver_chrome_webdriver_options.htm

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('--headless') # must options for Google Colab
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")


# In[3]:


MAGAZINE_NAME = "vietnamnet"
HOME_PAGE = "https://vietnamnet.vn/"


# # Thu thập dữ liệu

# In[4]:


driver = webdriver.Chrome(options=chrome_options)
# Vào trang web chính, mặc định phải chờ toàn bộ trang webload mới xong
driver.get(HOME_PAGE)


# In[5]:


# Lấy hết tất cả thể loại từ đây
cats = []

#### CODE
# row_menu = driver.find_elements(by=By.CLASS_NAME, value="header_submenu-content")
sub_menu = driver.find_element(by=By.CLASS_NAME, value="header_submenu-content-list")

cat_menus = sub_menu.find_elements(by=By.TAG_NAME, value="a")

for cat_name in cat_menus:
    cat = cat_name.get_attribute("title").strip()
    href = cat_name.get_attribute("href").strip()

    # bỏ qua logo-premium, logo-htvn
    if cat == "premium vietnamnet" or cat == "Hành trình Việt Nam":
        continue
    else:
        cats.append({"cat_names": cat, "url": href})
####


# In[6]:


cats, len(cats)


# In[7]:


TARGET_CATS = [
    "Chính trị",
    "Thời sự",
    "Kinh doanh",
    "Văn hóa - Giải trí",
    "Sức khỏe",
    "Pháp luật",
    "Thế giới",
    "Công nghệ",
    "Thể thao",
    "Du lịch",
    "Giáo dục"
]

filtered_cats = [c for c in cats if c['cat_names'] in TARGET_CATS]

print(len(filtered_cats))
for c in filtered_cats:
    print(c)


# # Thu thập URL bài báo

# In[8]:


NUM_ARTICLES_PER_CAT = 10 # có thể tăng lên

DATA_URL_FILE = "data/vietnamnet_url.json"

# Bổ sung cài đặt chromedriver
## Ta đặt load stategy ở đây là normal: https://www.selenium.dev/documentation/webdriver/drivers/options/
chrome_options.page_load_strategy = "normal"
driver = webdriver.Chrome(options=chrome_options)


# ## Chạy thật

# In[12]:


driver = webdriver.Chrome(options=chrome_options)


# In[13]:


NUM_ARTICLES_PER_CAT = 200
crawled_urls = set()
visited_pages = set()
WAIT = 8  # seconds

def _first_from_srcset(srcset_val: str):
    if not srcset_val:
        return None
    first_part = srcset_val.split(",")[0].strip()
    return first_part.split()[0] if first_part else None

def _first_non_empty(*vals):
    for v in vals:
        if v and v.strip() and not v.strip().startswith("data:image/"):
            return v.strip()
    return None

def _abs(href: str):
    return urljoin(HOME_PAGE, href) if href else None

def get_avatar_url_by_article_url(driver, article_url):
    try:
        avatar_divs = driver.find_elements(by=By.CLASS_NAME, value="verticalPost__avt")

        for avatar_div in avatar_divs:
            try:
                link_element = avatar_div.find_element(by=By.TAG_NAME, value="a")
                href = _abs(link_element.get_attribute("href"))  # <-- chuẩn hóa URL

                if href and href == article_url:
                    img_element = avatar_div.find_element(by=By.TAG_NAME, value="img")
                    img_url = _first_non_empty(
                        _first_from_srcset(img_element.get_attribute("data-srcset")),
                        _first_from_srcset(img_element.get_attribute("srcset")),
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

def _find_next_page_url(driver):
    """Tìm link trang kế tiếp an toàn, tránh hard-code [6]."""
    try:
        pag = driver.find_element(by=By.CLASS_NAME, value="pagination__list")
        # ưu tiên rel="next"
        nxt = pag.find_elements(by=By.CSS_SELECTOR, value='a[rel="next"]')
        if nxt:
            return _abs(nxt[0].get_attribute("href"))
        # hoặc li.active + li kế
        act = pag.find_elements(by=By.CSS_SELECTOR, value="li.active")
        if act:
            sib = act[0].find_elements(by=By.XPATH, value="following-sibling::li[1]/a")
            if sib:
                return _abs(sib[0].get_attribute("href"))
        # fallback: text 'Sau'/'Next'
        for a in pag.find_elements(by=By.TAG_NAME, value="a"):
            if (a.text or "").strip().lower() in {"sau", "next", "›", ">>"}:
                return _abs(a.get_attribute("href"))
    except NoSuchElementException:
        pass
    return None

def fill_missing_images_via_og(driver, items):
    """Bổ sung url_img còn thiếu bằng thẻ <meta property='og:image'> trong trang bài."""
    for it in items:
        if it.get("url_img"):
            continue
        try:
            driver.get(it["url"])
            metas = driver.find_elements(By.CSS_SELECTOR, 'meta[property="og:image"]')
            if metas:
                it["url_img"] = metas[0].get_attribute("content") or None
                if it["url_img"]:
                    print(f"Filled og:image for {it['url']}: {it['url_img']}")
        except Exception as e:
            print(f"OG fallback failed for {it['url']}: {e}")
    return items


def crawl_each_category_url(driver, category_url):
    all_data = []
    url = category_url

    # tránh lặp trang
    while (NUM_ARTICLES_PER_CAT is None or len(all_data) < NUM_ARTICLES_PER_CAT) and url and url not in visited_pages:
        visited_pages.add(url)
        driver.get(url)

        # # CHỜ tiêu đề xuất hiện để không bị miss
        # try:
        #     WebDriverWait(driver, WAIT).until(
        #         EC.presence_of_all_elements_located((By.CLASS_NAME, "vnn-title"))
        #     )
        # except TimeoutException:
        #     print("Timeout waiting for titles; stopping this category.")
        #     break

        title_news = driver.find_elements(by=By.CLASS_NAME, value="vnn-title")

        for title in title_news:
            try:
                a = title.find_element(by=By.TAG_NAME, value="a")
                url_new = _abs(a.get_attribute("href"))  # <-- chuẩn hóa
                if not url_new or not url_new.startswith(HOME_PAGE):
                    continue
                if url_new in crawled_urls:
                    continue

                avatar_url = get_avatar_url_by_article_url(driver, url_new)

                article_data = {
                    "url": url_new,
                    "url_img": avatar_url
                }
                all_data.append(article_data)
                crawled_urls.add(url_new)

                if NUM_ARTICLES_PER_CAT and len(all_data) >= NUM_ARTICLES_PER_CAT:
                    break

            except (StaleElementReferenceException, NoSuchElementException):
                continue
            except Exception as e:
                print(f"Error processing article: {e}")

        if NUM_ARTICLES_PER_CAT and len(all_data) >= NUM_ARTICLES_PER_CAT:
            break

        # PHÂN TRANG an toàn
        next_url = _find_next_page_url(driver)
        if not next_url or next_url in visited_pages:
            print("Cannot find next page or already visited, stopping crawl for this category")
            break
        url = next_url

    # thống kê để bạn theo dõi
    with_img = sum(1 for it in all_data if it.get("url_img"))
    print(f"[{category_url}] collected {len(all_data)} items, {with_img} with images, {len(all_data)-with_img} without.")
    return all_data



# In[14]:


saved_cats = {}
for cat in cats:
    cat_name = cat['cat_names']
    url = cat['url']
    if cat_name in TARGET_CATS:
        print(f"You are at {cat}.")
        article_data = crawl_each_category_url(driver, url)

        # thêm fallback ở đây
        article_data = fill_missing_images_via_og(driver, article_data)

        saved_cats[cat_name] = article_data


# In[15]:


DATA_URL_FILE = os.path.join("data", "vietnamnet_url_final.json")
os.makedirs(os.path.dirname(DATA_URL_FILE), exist_ok=True)

with open(DATA_URL_FILE, "w", encoding="utf-8") as fOut:
    json.dump(saved_cats, fOut, ensure_ascii=False, indent=4)

print(f"Đã lưu {sum(len(v) for v in saved_cats.values())} bài vào: {DATA_URL_FILE}")


# In[17]:


len(crawled_urls)


# # Thu thập thông tin bài báo

# ## Chạy thật

# In[71]:


import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def get_content_metadata(driver, article_url, url_img=None):
    """
    Extracts and returns metadata and content from a given article URL.

    :param driver: Selenium WebDriver instance.
    :param article_url: URL of the article to extract data from.
    :param url_img: (optional) URL of the article's thumbnail/cover image.
    :return: Dictionary containing article metadata and content.
    """

    # Get to current article
    driver.get(article_url)

    # Title & description
    title = driver.find_element(By.CSS_SELECTOR, "h1.content-detail-title").text.strip()
    description = driver.find_element(By.CLASS_NAME, "sm-sapo-mb-0").text.strip()

    # ---- Categories
    lis_cat = []
    try:
        cats = driver.find_element(By.CLASS_NAME, "sm-show-time")
        lis_cats = cats.find_elements(By.TAG_NAME, "li")
        lis_cats = lis_cats[1:]
        for cat in lis_cats:
            category = cat.text.strip()
            if category:
                lis_cat.append(category)
    except NoSuchElementException:
        pass

    main_cat = lis_cat[0] if lis_cat else "Unknown"
    sub_cat_val = lis_cat[-1] if len(lis_cat) > 1 else "None"

    # ---- Published date
    try:
        published_date = driver.find_element(By.CLASS_NAME, "bread-crumb-detail__time").text.strip()
    except NoSuchElementException:
        published_date = ""

    # ---- Content
    contents = []
    author_str = "Unknown"     # final string for author
    article = driver.find_element(By.CLASS_NAME, "main-content")
    children = article.find_elements(By.XPATH, "./*")

    for child in children:
        text = child.text.strip()
        if not text:
            continue

        if child.tag_name.lower() in {"p", "h1", "h2", "h3", "h4"}:
            contents.append(text)

        elif child.tag_name.lower() == "figure":
            # Caption (<=100) bọc trong [] ; dài hơn coi như đoạn nội dung
            if len(text) <= 100:
                contents.append(f"[{text}]")
            else:
                contents.append(text)
        # tables & others are ignored

    # ---- Author(s)
    authors = []
    try:
        wrapper = driver.find_element(By.CLASS_NAME, "article-detail-author-wrapper")
        author_names = wrapper.find_elements(By.CLASS_NAME, "name")
        for a in author_names:
            # ưu tiên <a title="...">, fallback text
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
        # fallback: cố gắng lấy dòng cuối giống dạng chữ ký tác giả
        if contents:
            last = contents[-1]
            dash_pos = last.find('-')
            if 0 <= dash_pos <= 30:
                # ví dụ: "Nguyễn A - Tổng hợp"
                possible = last[:dash_pos].strip()
                if possible:
                    author_str = possible

    return {
        "url": article_url,
        "url_img": url_img,                # <-- added
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


# In[ ]:


FILE_URL_PATH = "data/vietnamnet_url_final.json"  
MAX_ARTICLES_PER_CAT = None
DATA_FOLDER_OUTPUT = os.path.join("data", "vietnamnet_final")  
os.makedirs(DATA_FOLDER_OUTPUT, exist_ok=True)


# In[73]:


with open(FILE_URL_PATH, "r", encoding="utf-8") as fIn:
    url_data = json.load(fIn)

len(url_data)


# In[74]:


driver = webdriver.Chrome(options=chrome_options)

for cat, urls in url_data.items():
    print(f"Thu thập dữ liệu thể loại {cat} ..")
    count_crawled = 0
    cat_data = []

    for url in urls:
        try:
            # Giữ nguyên cấu trúc cũ, chỉ bổ sung url_img:
            if isinstance(url, dict):
                u = url.get("url")
                url_img = url.get("url_img")
            else:
                u = url
                url_img = None

            article = get_content_metadata(driver, u, url_img=url_img)
            cat_data.append(article)
            count_crawled += 1

            if MAX_ARTICLES_PER_CAT and count_crawled >= MAX_ARTICLES_PER_CAT:
                break

        except StaleElementReferenceException:
            print(f"Bug at url: {url}, with StaleElementReferenceException")
            driver.refresh()
            continue

        except NoSuchElementException:
            print(f"Bug at url: {url}, with NoSuchElementException")
            driver.refresh()
            continue

    # Lưu file JSON cho từng thể loại
    name_file_cat = cat.lower().replace(" ", "-") + ".json"
    out_path = os.path.join(DATA_FOLDER_OUTPUT, name_file_cat)
    with open(out_path, "w", encoding="utf-8") as fOut:
        json.dump(cat_data, fOut, ensure_ascii=False, indent=4)

driver.close()
print("Done.")


# In[ ]:




