#!/usr/bin/env python3
"""
CTV监控系统主脚本
整合新闻搜索、分析和报告
"""

import json
from datetime import datetime
from pathlib import Path
from news_fetcher import NewsFetcher

class CTVMonitor:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.fetcher = NewsFetcher(config_path)
        self.changes_log = []

    def load_known_entities(self):
        """加载已知实体"""
        entities_path = Path("known_entities.json")
        if entities_path.exists():
            with open(entities_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def analyze_article_changes(self, articles):
        """分析文章并识别重要变化"""
        changes = []

        for article in articles:
            categories = article.get('categories', [])
            companies = article.get('companies', [])

            # 重要变化检测
            if 'M&A' in categories:
                changes.append({
                    'type': 'M&A',
                    'severity': 'high',
                    'article': article,
                    'description': f"并购活动: {article['title']}"
                })

            if 'funding' in categories:
                changes.append({
                    'type': 'funding',
                    'severity': 'medium',
                    'article': article,
                    'description': f"融资动态: {article['title']}"
                })

            if 'product_launch' in categories:
                changes.append({
                    'type': 'product',
                    'severity': 'medium',
                    'article': article,
                    'description': f"产品发布: {article['title']}"
                })

            if 'earnings' in categories:
                changes.append({
                    'type': 'earnings',
                    'severity': 'low',
                    'article': article,
                    'description': f"财报信息: {article['title']}"
                })

            # 特定公司关注
            for company in companies:
                if company.lower() in ['netflix', 'amazon', 'walmart', 'google']:
                    changes.append({
                        'type': 'company_update',
                        'severity': 'medium',
                        'company': company,
                        'article': article,
                        'description': f"{company}更新: {article['title']}"
                    })

        return changes

    def run_daily_check(self, hours=24):
        """运行每日检查"""
        print(f"\n{'='*60}")
        print(f"CTV监控开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"搜索最近 {hours} 小时的新闻")
        print(f"{'='*60}\n")

        # 获取新闻
        articles = self.fetcher.run_full_check(hours)

        if not articles:
            print("未找到相关文章")
            return self._generate_empty_report()

        # 分析变化
        changes = self.analyze_article_changes(articles)

        # 生成报告
        report = self._generate_report(articles, changes)

        # 保存报告
        self._save_report(report)

        print(f"\n{'='*60}")
        print(f"✅ 监控完成")
        print(f"  - 总文章数: {len(articles)}")
        print(f"  - 重要变化: {len(changes)}")
        print(f"{'='*60}\n")

        return report

    def _generate_report(self, articles, changes):
        """生成报告"""
        entities_data = self.load_known_entities()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_articles": len(articles),
                "companies_tracked": len(entities_data['companies']['known_entities']) if entities_data else 0,
                "changes_detected": len(changes),
                "categories": self._count_categories(articles)
            },
            "important_changes": changes[:20],  # 最多20个重要变化
            "all_articles": articles,
            "top_sources": self._get_top_sources(articles)
        }

        return report

    def _generate_empty_report(self):
        """生成空报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_articles": 0,
                "companies_tracked": 0,
                "changes_detected": 0,
                "status": "no_articles_found"
            },
            "important_changes": [],
            "all_articles": [],
            "note": "未找到相关文章，可能是：1) 搜索时间范围太短 2) 网络问题 3) RSS源暂时不可用"
        }

    def _count_categories(self, articles):
        """统计分类"""
        category_count = {}
        for article in articles:
            for category in article.get('categories', ['general']):
                category_count[category] = category_count.get(category, 0) + 1
        return category_count

    def _get_top_sources(self, articles):
        """获取主要来源"""
        source_count = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            source_count[source] = source_count.get(source, 0) + 1

        # 排序并返回前10
        return dict(sorted(source_count.items(), key=lambda x: x[1], reverse=True)[:10])

    def _save_report(self, report):
        """保存报告"""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存带时间戳的报告
        report_path = reports_dir / f"monitor_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 保存最新报告
        with open(reports_dir / "latest_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 报告已保存:")
        print(f"   - {report_path}")
        print(f"   - {reports_dir / 'latest_report.json'}")


def main():
    """主函数"""
    import sys

    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except:
            pass

    monitor = CTVMonitor()
    monitor.run_daily_check(hours)


if __name__ == "__main__":
    main()
