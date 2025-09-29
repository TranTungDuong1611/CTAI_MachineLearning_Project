import re
import time
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class DanTriCrawler:
    def __init__(self):
        self.BASE = "https://dantri.com.vn"
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
        }
        self.TIMEOUT = 25

        self.CATEGORIES = {
            "Xã hội": "/xa-hoi.htm",
            "Kinh doanh": "/kinh-doanh.htm",
            "Đời sống": "/doi-song.htm",
            "Sức khỏe": "/suc-khoe.htm",
            "Pháp luật": "/phap-luat.htm",
            "Thế giới": "/the-gioi.htm",
            "Khoa học": "/khoa-hoc.htm",
            "Thể thao": "/the-thao.htm",
            "Giải trí": "/giai-tri.htm",
            "Du lịch": "/du-lich.htm",
            "Giáo dục": "/giao-duc.htm"
        }

        self.MAX_PAGES_PER_CAT = 10

        self.ARTICLE_LINK_SELECTORS = [
            "h3 a[href*='.htm']",
            "article a[href*='.htm']",
            "a.article-title[href*='.htm']",
            "a.dt-news__title[href*='.htm']"
        ]

        self.CONTENT_CONTAINERS = [
            "article",
            "div#dantri-detail-content",
            "div.dt-detail__content",
            "div.detail__content",
            "div.singular-content",
            "div.article__content",
            "div[itemprop='articleBody']",
        ]

        self.IMG_ATTRS = ["data-src", "data-original", "data-echo", "src", "data-srcset", "srcset"]
        self.VALID_IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")
        self.EXCLUDE_IN_PATH = {"video", "clip", "photo", "infographic", "podcast", "tag"}
        self.PAGE_TAIL_RE = re.compile(r"(-trang-\d+\.htm$|-p\d+\.htm$)", re.I)

        self.KILL_PREFIXES = [
            "ảnh:", "video:", "xem thêm", "mời độc giả", "độc giả", "bình luận",
            "theo:", "nguồn:", "liên hệ quảng cáo", "xem thêm về:"
        ]
        self.KILL_REGEX = re.compile(r"^\s*(%s)" % "|".join([re.escape(k) for k in self.KILL_PREFIXES]), re.I)

    def get_soup(self, url, retries=3, backoff=0.6):
        """Get BeautifulSoup object from URL with retry logic"""
        last_err = None
        for k in range(retries):
            try:
                r = requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
                r.encoding = "utf-8"
                r.raise_for_status()
                return BeautifulSoup(r.text, "html.parser")
            except Exception as e:
                last_err = e
                print(f"  ! Retry {k+1}/{retries} failed for {url}: {e}")
                time.sleep(backoff * (k + 1))
        raise last_err

    def clean_url(self, href, base=None):
        """Clean and normalize URL"""
        if not href:
            return None
        href = href.strip()
        if href.startswith("#"):
            return None
        return urljoin(base or self.BASE, href)

    def is_same_domain(self, url, domain="dantri.com.vn"):
        """Check if URL belongs to the same domain"""
        try:
            return urlparse(url).netloc.endswith(domain)
        except:
            return False

    def path_parts(self, url):
        """Get path parts from URL"""
        return [x for x in urlparse(url).path.split("/") if x]

    def is_article_url(self, href):
        """Check if URL is a valid article URL"""
        if not href:
            return False
        if not href.endswith(".htm"):
            return False
        parts = self.path_parts(href)
        if any(x in parts for x in self.EXCLUDE_IN_PATH):
            return False
        if self.PAGE_TAIL_RE.search(urlparse(href).path):
            return False
        return True

    def find_next_page_url(self, soup):
        """Find next page URL from soup"""
        ln = soup.find("link", rel=lambda x: x and "next" in x.lower())
        if ln and ln.get("href"):
            return self.clean_url(ln["href"])

        a = soup.select_one(
            "a[rel='next'], a.next, a[aria-label*='Next' i], a[aria-label*='Sau' i], "
            "li.pagination__next a[href], a[title*='Sau' i]"
        )
        if a and a.get("href"):
            return self.clean_url(a["href"])

        for a in soup.find_all("a"):
            txt = (a.get_text() or "").strip().lower()
            if any(k in txt for k in ["sau", "next", "trang sau", "»", ">"]):
                if a.get("href"):
                    return self.clean_url(a["href"])
        return None

    def _parse_srcset(self, val):
        """Parse srcset attribute"""
        if not val:
            return []
        return [p.strip().split(" ")[0] for p in val.split(",") if p.strip()]

    def _pick_best_from_srcset(self, val):
        """Pick best image URL from srcset"""
        if not val:
            return None
        best_url, best_w = None, -1
        for part in val.split(","):
            toks = part.strip().split()
            if not toks:
                continue
            url = toks[0]
            width = -1
            for t in toks[1:]:
                m = re.match(r"(\d+)(w|x)$", t)
                if m:
                    width = int(m.group(1))
                    break
            if width > best_w:
                best_w = width
                best_url = url
        return self.clean_url(best_url)

    def parse_listing_articles(self, cat_url, delay=0.25, max_pages=None):
        """Parse article listings from category page"""
        out, visited = [], set()
        url, page_count = self.clean_url(cat_url), 0

        while url and url not in visited:
            visited.add(url)
            soup = self.get_soup(url)

            found, page_links = 0, []
            for sel in self.ARTICLE_LINK_SELECTORS:
                for a in soup.select(sel):
                    href = self.clean_url(a.get("href"))
                    if not href or not self.is_same_domain(href) or not self.is_article_url(href):
                        continue
                    if href in page_links:
                        continue
                    page_links.append(href)
                    out.append({"title": a.get_text(strip=True) or "", "link": href})
                    found += 1

            print(f"    -> Found {found} article links at:", url)

            next_url = self.find_next_page_url(soup)
            if not next_url:
                break
            url = next_url
            page_count += 1
            if max_pages is not None and page_count >= max_pages:
                break
            time.sleep(delay)

        uniq = {}
        for r in out:
            if r["link"] not in uniq:
                uniq[r["link"]] = r
        return list(uniq.values())

    def extract_article(self, article_url):
        """Extract article content from URL"""
        soup = self.get_soup(article_url)

        # Title
        title = ""
        h1 = soup.select_one("h1")
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)
        if not title:
            og = soup.select_one("meta[property='og:title']")
            if og and og.get("content"):
                title = og["content"].strip()
        if not title:
            tt = soup.find("title")
            if tt:
                title = tt.get_text(strip=True)

        # Content container
        container = None
        for sel in self.CONTENT_CONTAINERS:
            container = soup.select_one(sel)
            if container and container.find(["p", "li", "img"]):
                break
        if not container:
            container = soup.body or soup

        # Content text
        paras = []
        for tag in container.find_all(["p", "li"]):
            t = tag.get_text(" ", strip=True)
            if not t:
                continue
            if self.KILL_REGEX.search(t):
                continue
            if re.match(r"^\s*xem thêm\s*:?", t, flags=re.I):
                continue
            if len(t) < 20:
                continue
            paras.append(t)
        content = "\n".join(paras).strip()
        if not content:
            return None

        # Hero image
        hero = ""
        for meta_sel in ["meta[property='og:image']", "meta[name='twitter:image']"]:
            ogimg = soup.select_one(meta_sel)
            if ogimg and ogimg.get("content"):
                u = self.clean_url(ogimg["content"])
                if u:
                    hero = u
                    break
        if not hero:
            first_img = container.find("img")
            if first_img:
                if first_img.get("srcset") or first_img.get("data-srcset"):
                    best = self._pick_best_from_srcset(first_img.get("srcset") or first_img.get("data-srcset"))
                    if best:
                        hero = best
                if not hero:
                    for attr in self.IMG_ATTRS:
                        val = first_img.get(attr)
                        if val:
                            if "srcset" in attr:
                                for cand in self._parse_srcset(val):
                                    cu = self.clean_url(cand)
                                    if cu:
                                        hero = cu
                                        break
                                if hero:
                                    break
                            else:
                                cu = self.clean_url(val)
                                if cu:
                                    hero = cu
                                    break

        # Published date and author
        published_date, author = "", ""
        for sel in [
            'meta[property="article:published_time"]',
            'meta[name="pubdate"]',
            'meta[itemprop="datePublished"]',
            'time[datetime]'
        ]:
            tag = soup.select_one(sel)
            if tag:
                published_date = (tag.get("content") or tag.get("datetime") or "").strip()
                if published_date:
                    break

        auth_tag = soup.select_one('meta[name="author"], a[rel="author"], .author, .dt-news__author, .article__author')
        if auth_tag:
            author = (auth_tag.get("content") or auth_tag.get_text(" ", strip=True) or "").strip()

        return title.strip(), content.strip(), (hero or ""), (published_date or ""), (author or "")

    def run_crawl(self, per_article_delay=0.15, max_pages_root=None, out_json="dantri_articles_root.json"):
        """Run the complete crawling process"""
        records, seen_urls = [], set()
        max_pages_root = max_pages_root or self.MAX_PAGES_PER_CAT

        print("CATEGORIES:", {k: urljoin(self.BASE, v) for k, v in self.CATEGORIES.items()})

        for cat_name, cat_path in self.CATEGORIES.items():
            cat_url = urljoin(self.BASE, cat_path)
            print(f"\n=== {cat_name} => {cat_url}")
            links = self.parse_listing_articles(cat_url, delay=0.25, max_pages=max_pages_root)
            print(f"  + root listing: {len(links)} links")

            for i, item in enumerate(links, 1):
                if item["link"] in seen_urls:
                    continue
                seen_urls.add(item["link"])

                try:
                    parsed = self.extract_article(item["link"])
                except Exception as e:
                    print(f"  ! Parse error: {item['link']} -> {e}")
                    continue
                if not parsed:
                    continue
                title, content, hero, pub, author = parsed

                rec = {
                    "url": item["link"],
                    "image-url": hero,
                    "title": title or item["title"],
                    "content": content,
                    "metadata": {
                        "cat": cat_name,
                        "published_date": pub,
                        "author": author
                    }
                }
                records.append(rec)

                if i % 10 == 0 or i == len(links):
                    print(f"    [{i}/{len(links)}] root {cat_name}")

                time.sleep(per_article_delay)

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"\nSaved JSON: {out_json} (total records: {len(records)})")
        return records


if __name__ == "__main__":
    crawler = DanTriCrawler()
    crawler.run_crawl(
        per_article_delay=0.15,
        max_pages_root=10,
        out_json="data/raw_data/dantri/dantri_articles_root.json"
    )