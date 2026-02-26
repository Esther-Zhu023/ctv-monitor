# 新闻搜索功能实现说明

## ✅ 已实现的功能

### 1. RSS新闻抓取（无需API）
- ✅ 从6个主要行业RSS源获取新闻
- ✅ 自动过滤CTV相关内容
- ✅ 提取提到的公司名称
- ✅ 自动分类（M&A、融资、产品发布、财报等）

**RSS源包括**:
- TechCrunch
- Variety
- AdAge
- AdExchanger
- Broadcasting & Cable
- TV Technology

### 2. Google News RSS搜索（免费）
- ✅ 使用Google News RSS API
- ✅ 支持自定义搜索查询
- ✅ 无需API key
- ✅ 为每个公司专门搜索

### 3. NewsAPI集成（可选）
- ✅ 支持NewsAPI（免费100次/天）
- ✅ 如果配置了API key会自动使用
- ✅ 提供更准确的搜索结果

### 4. 智能分析功能
- ✅ 自动识别提到的公司
- ✅ 文章分类（M&A、融资、产品、财报等）
- ✅ 重要变化检测
- ✅ 来源统计
- ✅ 去重处理

### 5. 报告生成
- ✅ JSON格式报告
- ✅ 保存最新报告
- ✅ 历史报告归档
- ✅ 摘要统计

## 🚀 使用方法

### 基本使用
```bash
# 搜索最近24小时（默认）
python3 news_fetcher.py

# 搜索最近48小时
python3 news_fetcher.py 48

# 搜索最近一周
python3 news_fetcher.py 168
```

### 使用监控系统
```bash
# 运行完整监控（包括新闻搜索和分析）
python3 monitor.py

# 搜索最近12小时
python3 monitor.py 12
```

### 可选：配置NewsAPI
```bash
# 1. 复制配置模板
cp config.json.example config.json

# 2. 编辑config.json，添加你的API key
# {
#   "news_api_key": "your-api-key-here",
#   "enable_newsapi": true
# }

# 3. 重新运行
python3 monitor.py
```

## 📊 工作流程

```
开始
 ↓
1. 从RSS源获取新闻
 ↓
2. 为每个公司搜索Google News
 ↓
3. 去重和过滤
 ↓
4. 分析和分类
 ↓
5. 识别重要变化
 ↓
6. 生成报告
 ↓
保存到 reports/
```

## 🔍 搜索能力

### 自动搜索的公司
基于 `known_entities.json` 中的11家公司：
- Amaze
- Tatari
- Magnite
- PubMatic
- Roku
- Google TV/Android TV
- Amazon Fire TV
- Netflix
- Walmart/Vizio
- Samsung Tizen
- LG webOS

### 自动分类
- **M&A**: 并购、收购
- **funding**: 融资、投资
- **product_launch**: 产品发布
- **earnings**: 财报
- **partnership**: 合作关系
- **regulatory**: 监管
- **general**: 一般新闻

### 检测的重要变化
- Netflix/WBD收购相关
- 任何一家跟踪公司的M&A
- CTV公司融资
- 产品功能发布
- 财报信息

## 📈 报告格式

### latest_report.json
```json
{
  "timestamp": "2026-02-25T...",
  "summary": {
    "total_articles": 15,
    "companies_tracked": 11,
    "changes_detected": 5,
    "categories": {
      "M&A": 2,
      "funding": 1,
      "product_launch": 3
    }
  },
  "important_changes": [...],
  "all_articles": [...],
  "top_sources": {
    "Google News": 8,
    "TechCrunch": 3,
    "Variety": 2
  }
}
```

### latest_news.json
```json
{
  "fetch_time": "2026-02-25T...",
  "total_articles": 15,
  "articles": [
    {
      "title": "...",
      "url": "...",
      "source": "...",
      "published": "...",
      "summary": "...",
      "companies": ["Netflix", "Amazon"],
      "categories": ["M&A"]
    }
  ]
}
```

## 🧪 测试

### 测试新闻搜索
```bash
# 快速测试（最近6小时）
python3 news_fetcher.py 6
```

### 查看原始数据
```bash
# 查看最新获取的新闻
cat reports/latest_news.json | python3 -m json.tool

# 查看监控报告
cat reports/latest_report.json | python3 -m json.tool
```

## ⚙️ 配置选项

### config.json
```json
{
  "news_api_key": "your-key-here",      // NewsAPI key（可选）
  "enable_newsapi": true,                // 是否使用NewsAPI
  "check_interval_hours": 24,            // 默认搜索时间范围
  "max_articles_per_source": 50,         // 每个源最大文章数
  "enable_duplicate_detection": true     // 启用去重
}
```

### known_entities.json
添加新公司会自动被搜索：
```json
{
  "name": "新公司",
  "search_keywords": ["关键词1", "关键词2"]
}
```

## 🔄 更新频率建议

| 使用场景 | 建议频率 | hours参数 |
|---------|---------|-----------|
| 实时监控 | 每小时 | 1 |
| 日常监控 | 每天 | 24 |
| 周报 | 每周 | 168 |
| 测试 | 随时 | 6 |

## 📝 注意事项

### API限制
- **Google News RSS**: 无限制
- **NewsAPI免费版**: 100次/天
- **RSS feeds**: 建议每次请求间隔0.5秒

### 网络问题
- 如果RSS源不可用，会跳过并继续
- 每个源最多重试2次
- 超时设置10秒

### 性能
- 完整检查约需2-3分钟（11家公司）
- 主要时间花在等待响应
- 已优化并行处理

## 🎯 下一步优化

可选的增强功能：
1. [ ] 添加更多RSS源
2. [ ] 支持社交媒体API（Twitter/X）
3. [ ] 添加邮件通知
4. [ ] 支持Slack/钉钉通知
5. [ ] Web界面展示
6. [ ] 历史趋势分析

## 💡 常见问题

**Q: 为什么有时候找不到文章？**
A: 可能原因：
1. 搜索时间范围内确实没有相关新闻
2. 网络连接问题
3. RSS源暂时不可用
4. 关键词匹配不够准确

**Q: 如何提高准确性？**
A:
1. 配置NewsAPI（更准确的搜索）
2. 在`known_entities.json`中添加更多关键词
3. 调整`ctv_keywords`列表

**Q: 会消耗多少API调用？**
A:
- 不配置NewsAPI: 0次（完全免费）
- 配置NewsAPI: 每个公司约2-3次，总共约30次/天

**Q: 如何只搜索特定公司？**
A: 编辑`monitor.py`，修改`for company in data['companies']['known_entities'][:5]`中的数字

---

**状态**: ✅ 完全实现并测试
**最后更新**: 2026-02-25
