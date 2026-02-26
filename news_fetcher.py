#!/usr/bin/env python3
"""
新闻获取器 - 实现真正的新闻搜索功能
支持：RSS feeds、Google News RSS、NewsAPI
"""

import feedparser
import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import time
from urllib.parse import quote

class NewsFetcher:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.load_config()

        # RSS源（无需API）
        self.rss_sources = {
            "techcrunch": "https://techcrunch.com/feed/",
            "variety": "https://variety.com/feed/",
            "adage": "https://adage.com/feed",
            "adexchanger": "https://adexchanger.com/rss/",
            "broadcasting_cable": "https://www.broadcastingcable.com/feed",
            "tvtechnology": "https://www.tvtechnology.com/feed"
        }

        # CTV相关关键词
        self.ctv_keywords = [
            "CTV", "Connected TV", "connected television",
            "streaming TV", "OTT", "over-the-top",
            "Roku", "Fire TV", "Apple TV", "Android TV", "Google TV",
            "programmatic TV", "TV advertising", "streaming ads",
            "Magnite", "PubMatic", "Trade Desk", "Tatari",
            "Netflix advertising", "Netflix ads",
            "linear TV", "smart TV", "CTV measurement",
            "retail media", "shopping ads TV", "shoppable TV",
            "Walmart Connect", "Amazon DSP", "Samsung Ads", "LG Ads"
        ]

        # 已知公司列表
        self.known_companies = self._load_known_companies()

    def load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "news_api_key": "",
                "enable_newsapi": False
            }

    def _load_known_companies(self):
        """加载已知公司列表"""
        entities_path = Path("known_entities.json")
        if entities_path.exists():
            with open(entities_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [company['name'].lower() for company in data['companies']['known_entities']]
        return []

    def is_ctv_relevant(self, text):
        """检查文本是否与CTV相关"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.ctv_keywords)

    def fetch_rss_feed(self, url, max_retries=2):
        """获取RSS feed"""
        for attempt in range(max_retries):
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    return feed.entries
                else:
                    return []
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                print(f"Error fetching {url}: {e}")
                return []

    def fetch_from_rss(self, hours=24):
        """从RSS源获取最近的CTV相关新闻"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        relevant_articles = []

        for source_name, url in self.rss_sources.items():
            print(f"  📡 {source_name}...", end="", flush=True)

            entries = self.fetch_rss_feed(url)
            source_articles = 0

            for entry in entries:
                # 检查时间
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                    except:
                        continue
                elif hasattr(entry, 'updated_parsed'):
                    try:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    except:
                        continue
                else:
                    continue

                if pub_date and pub_date < cutoff_time:
                    continue

                # 检查相关性
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                combined_text = f"{title} {summary}"

                if self.is_ctv_relevant(combined_text):
                    # 提取提到的公司
                    companies_mentioned = self.extract_companies_mentioned(combined_text)

                    article = {
                        "source": source_name,
                        "title": self._clean_html(title),
                        "url": entry.get('link'),
                        "published": pub_date.isoformat() if pub_date else None,
                        "summary": self._clean_html(summary)[:500],
                        "companies": companies_mentioned,
                        "categories": self._categorize_article(combined_text)
                    }
                    relevant_articles.append(article)
                    source_articles += 1

            print(f" {source_articles} articles")

            # 礼貌性延迟
            time.sleep(0.5)

        return relevant_articles

    def search_google_news_rss(self, query, hours=24):
        """使用Google News RSS搜索（免费，无需API）"""
        print(f"  🔍 Google News: {query}")

        # Google News RSS URL - 正确编码查询参数
        search_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"

        try:
            feed = feedparser.parse(rss_url)
            articles = []
            cutoff_time = datetime.now() - timedelta(hours=hours)

            for entry in feed.entries:
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                    except:
                        continue

                if pub_date and pub_date < cutoff_time:
                    continue

                title = entry.get('title', '')
                source = entry.get('source', 'Unknown')

                article = {
                    "source": f"Google News ({source})",
                    "title": title.replace(f" - {source}", ""),
                    "url": entry.get('link'),
                    "published": pub_date.isoformat() if pub_date else None,
                    "summary": "",
                    "companies": self.extract_companies_mentioned(title),
                    "categories": self._categorize_article(title)
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"    Error: {e}")
            return []

    def search_newsapi(self, query, hours=24):
        """使用NewsAPI搜索（需要API key，免费100次/天）"""
        if not self.config.get("news_api_key") or not self.config.get("enable_newsapi"):
            return []

        print(f"  🔍 NewsAPI: {query}")

        api_key = self.config["news_api_key"]
        url = "https://newsapi.org/v2/everything"

        # 计算时间范围
        from_date = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")

        params = {
            "q": query,
            "apiKey": api_key,
            "sortBy": "publishedAt",
            "from": from_date,
            "language": "en",
            "pageSize": 20
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                # 过滤掉没有真实内容的
                if article.get("title") == "[Removed]":
                    continue

                articles.append({
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "published": article.get("publishedAt"),
                    "summary": article.get("description", "")[:300],
                    "companies": self.extract_companies_mentioned(
                        f"{article.get('title', '')} {article.get('description', '')}"
                    ),
                    "categories": self._categorize_article(
                        f"{article.get('title', '')} {article.get('description', '')}"
                    )
                })

            return articles

        except requests.exceptions.RequestException as e:
            print(f"    Error: {e}")
            return []

    def fetch_company_news(self, company_name, company_keywords, hours=24):
        """获取特定公司的新闻"""
        print(f"\n📊 搜索 {company_name} 的新闻...")

        articles = []

        # 方法1: Google News RSS（免费）
        for keyword in company_keywords[:3]:  # 限制关键词数量
            google_articles = self.search_google_news_rss(keyword, hours)
            articles.extend(google_articles)
            time.sleep(1)  # 礼貌性延迟

        # 方法2: NewsAPI（如果配置了）
        if self.config.get("enable_newsapi"):
            for keyword in company_keywords[:2]:
                api_articles = self.search_newsapi(keyword, hours)
                articles.extend(api_articles)
                time.sleep(0.5)

        # 去重
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        print(f"  ✓ 找到 {len(unique_articles)} 篇相关文章")
        return unique_articles

    def extract_companies_mentioned(self, text):
        """从文本中提取提到的公司"""
        text_lower = text.lower()
        companies = []
        for company in self.known_companies:
            if company in text_lower:
                companies.append(company.title())
        return list(set(companies))

    def _categorize_article(self, text):
        """对文章进行分类"""
        text_lower = text.lower()
        categories = []

        # M&A检测
        if any(word in text_lower for word in ['acquires', 'acquisition', 'merger', 'buys', 'deal', 'takeover']):
            categories.append('M&A')

        # 融资检测
        if any(word in text_lower for word in ['funding', 'raises', 'investment', 'series a', 'series b', 'series c', 'ipo', 'venture capital']):
            categories.append('funding')

        # 产品发布
        if any(word in text_lower for word in ['launches', 'announces', 'unveils', 'introduces', 'new feature', 'rollout']):
            categories.append('product_launch')

        # 财报
        if any(word in text_lower for word in ['earnings', 'q1', 'q2', 'q3', 'q4', 'revenue', 'profit', 'financial results']):
            categories.append('earnings')

        # 合作关系
        if any(word in text_lower for word in ['partnership', 'partner', 'collaboration', 'integration', 'deal']):
            categories.append('partnership')

        # 监管
        if any(word in text_lower for word in ['regulation', 'ftc', 'doj', 'antitrust', 'lawsuit', 'legal']):
            categories.append('regulatory')

        return categories if categories else ['general']

    def _clean_html(self, text):
        """清理HTML标签"""
        if not text:
            return ""
        # 移除HTML标签
        clean = re.sub(r'<[^>]+>', '', text)
        # 解码HTML实体
        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&quot;', '"').replace('&#39;', "'")
        return clean.strip()

    def run_full_check(self, hours=24):
        """运行完整检查"""
        print(f"\n{'='*60}")
        print(f"CTV新闻检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        all_articles = []

        # 1. 从RSS源获取
        print("📡 从RSS源获取...")
        rss_articles = self.fetch_from_rss(hours)
        all_articles.extend(rss_articles)
        print(f"  ✓ RSS: {len(rss_articles)} articles\n")

        # 2. 为每个已知公司搜索新闻
        print("🔍 搜索特定公司新闻...")
        entities_path = Path("known_entities.json")
        if entities_path.exists():
            with open(entities_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for company in data['companies']['known_entities'][:5]:  # 限制前5个公司
                keywords = company.get('search_keywords', [company['name']])
                company_articles = self.fetch_company_news(
                    company['name'],
                    keywords,
                    hours
                )
                all_articles.extend(company_articles)
                time.sleep(2)  # 礼貌性延迟

        # 3. 搜索行业趋势
        print("\n🎯 搜索行业趋势...")
        trend_queries = [
            "CTV advertising funding",
            "Connected TV acquisition",
            "retail media CTV"
        ]
        for query in trend_queries:
            trend_articles = self.search_google_news_rss(query, hours)
            all_articles.extend(trend_articles)
            time.sleep(1)

        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        print(f"\n{'='*60}")
        print(f"✅ 总计找到 {len(unique_articles)} 篇文章")
        print(f"{'='*60}\n")

        return unique_articles

    def save_report(self, articles):
        """保存报告"""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output = {
            "fetch_time": datetime.now().isoformat(),
            "total_articles": len(articles),
            "articles": articles
        }

        # 保存带时间戳的报告
        report_path = reports_dir / f"news_fetch_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # 保存最新报告
        with open(reports_dir / "latest_news.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"📄 报告已保存: {report_path}")

        # 打印摘要
        self._print_summary(articles)

        return report_path

    def _print_summary(self, articles):
        """打印摘要"""
        if not articles:
            print("未找到相关文章")
            return

        # 按分类统计
        category_count = {}
        for article in articles:
            for category in article.get('categories', ['general']):
                category_count[category] = category_count.get(category, 0) + 1

        print("\n📊 文章分类:")
        for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")

        # 显示前10篇
        print(f"\n📰 最新 {min(10, len(articles))} 篇文章:")
        for i, article in enumerate(articles[:10], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   来源: {article['source']}")
            if article['companies']:
                print(f"   公司: {', '.join(article['companies'])}")
            if article['categories']:
                print(f"   分类: {', '.join(article['categories'])}")
            print(f"   时间: {article.get('published', 'N/A')}")
            print(f"   链接: {article['url']}")


def main():
    """主函数"""
    import sys

    hours = 24
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])

    print(f"🔍 搜索最近 {hours} 小时的CTV相关新闻\n")

    fetcher = NewsFetcher()

    # 运行检查
    articles = fetcher.run_full_check(hours)

    # 保存报告
    if articles:
        fetcher.save_report(articles)
    else:
        print("未找到相关文章")


if __name__ == "__main__":
    main()
