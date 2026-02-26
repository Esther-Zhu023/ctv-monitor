#!/bin/bash
# 检查CTV监控状态

echo "📊 CTV监控系统状态"
echo "=================="
echo ""

# 检查launchd
echo "📱 Launchd服务状态:"
if launchctl list | grep -q "com.ctvmonitor"; then
    echo "   ✅ 运行中"
    launchctl list | grep "com.ctvmonitor"
else
    echo "   ❌ 未运行"
fi

echo ""

# 检查cron
echo "⏰ Cron任务状态:"
if crontab -l 2>/dev/null | grep -q "CTV_Monitor"; then
    echo "   ✅ 已配置"
    crontab -l | grep "CTV_Monitor"
else
    echo "   ❌ 未配置"
fi

echo ""

# 检查日志
echo "📋 最近日志 (最后10行):"
if [ -f "logs/monitor.log" ]; then
    echo "   --- monitor.log ---"
    tail -5 logs/monitor.log | sed 's/^/   /'
else
    echo "   ℹ️  日志文件不存在"
fi

echo ""

# 检查最新报告
echo "📄 最新报告:"
if [ -f "reports/latest_report.json" ]; then
    REPORT_DATE=$(python3 -c "import json; f=open('reports/latest_report.json'); d=json.load(f); print(d.get('date', d.get('report_date', 'Unknown')))" 2>/dev/null)
    REPORT_SIZE=$(du -h reports/latest_report.json | cut -f1)
    echo "   📅 日期: $REPORT_DATE"
    echo "   📦 大小: $REPORT_SIZE"
else
    echo "   ℹ️  报告不存在，首次运行: python3 monitor.py"
fi

echo ""

# 检查依赖
echo "🔧 Python依赖:"
python3 -c "import feedparser, requests" 2>/dev/null && echo "   ✅ 依赖已安装" || echo "   ❌ 缺少依赖，运行: pip3 install feedparser requests"

echo ""
echo "💡 管理命令:"
echo "   启动自动化: bash start.sh"
echo "   停止自动化: bash stop.sh"
echo "   手动运行:   python3 monitor.py"
echo "   查看日志:   tail -f logs/monitor.log"
