#!/bin/bash
# CTV监控自动化设置脚本

echo "🚀 CTV监控系统 - 自动化配置"
echo "================================"

# 检查目录
cd /Users/zhuxiaolin/CTV_Monitor

# 确保日志目录存在
mkdir -p logs

# 安装依赖
echo "📦 检查依赖..."
pip3 install -q feedparser requests python-dateutil 2>/dev/null

# 测试运行
echo "🧪 测试运行监控脚本..."
python3 monitor.py

echo ""
echo "✅ 自动化配置选项："
echo ""
echo "1. 使用 launchd (macOS推荐) - 每天早上9:00运行"
echo "2. 使用 cron - 每天9:00运行"
echo "3. 手动运行 - 不设置自动化"
echo ""
read -p "选择选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📱 配置 launchd 服务..."

        # 创建launchd目录
        LAUNCH_DIR="$HOME/Library/LaunchAgents"
        mkdir -p "$LAUNCH_DIR"

        # 复制plist文件
        cp launchd/com.ctvmonitor.plist "$LAUNCH_DIR/"

        # 加载服务
        launchctl load "$LAUNCH_DIR/com.ctvmonitor.plist"

        echo "✅ launchd服务已配置并启动！"
        echo ""
        echo "📋 服务信息："
        echo "   - 每天 9:00 AM 自动运行"
        echo "   - 日志位置: logs/monitor.log"
        echo "   - 错误日志: logs/error.log"
        echo ""
        echo "🔍 管理命令："
        echo "   查看状态: launchctl list | grep ctvmonitor"
        echo "   停止服务: launchctl unload $LAUNCH_DIR/com.ctvmonitor.plist"
        echo "   重启服务: launchctl unload $LAUNCH_DIR/com.ctvmonitor.plist && launchctl load $LAUNCH_DIR/com.ctvmonitor.plist"
        echo "   查看日志: tail -f logs/monitor.log"
        ;;

    2)
        echo ""
        echo "⏰ 配置 cron 任务..."

        # 获取当前crontab
        crontab -l > /tmp/crontab_backup_$$ 2>/dev/null || true

        # 添加新的cron任务
        (crontab -l 2>/dev/null; echo "0 9 * * * cd /Users/zhuxiaolin/CTV_Monitor && /usr/bin/python3 monitor.py >> logs/cron.log 2>&1") | crontab -

        echo "✅ cron任务已配置！"
        echo ""
        echo "📋 任务信息："
        echo "   - 每天 9:00 AM 自动运行"
        echo "   - 日志位置: logs/cron.log"
        echo ""
        echo "🔍 管理命令："
        echo "   查看任务: crontab -l"
        echo "   编辑任务: crontab -e"
        echo "   删除任务: crontab -e (然后删除相关行)"
        echo "   查看日志: tail -f logs/cron.log"
        ;;

    3)
        echo ""
        echo "ℹ️  手动运行模式"
        echo ""
        echo "运行命令："
        echo "  cd /Users/zhuxiaolin/CTV_Monitor"
        echo "  python3 monitor.py"
        ;;

    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "📁 报告位置: reports/latest_report.json"
echo "📖 快速参考: QUICK_REFERENCE.md"
echo ""
echo "🎉 配置完成！"
