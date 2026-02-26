#!/bin/bash
# 停止CTV监控自动化

echo "🛑 停止CTV监控自动化"
echo "===================="

LAUNCH_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_DIR/com.ctvmonitor.plist"

# 检查launchd服务
if launchctl list | grep -q "com.ctvmonitor"; then
    echo "📱 停止 launchd 服务..."
    launchctl unload "$PLIST_FILE"
    echo "✅ launchd服务已停止"

    # 询问是否删除配置文件
    read -p "是否删除配置文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$PLIST_FILE"
        echo "🗑️  配置文件已删除"
    fi
else
    echo "ℹ️  launchd服务未运行"
fi

# 检查cron任务
if crontab -l 2>/dev/null | grep -q "CTV_Monitor"; then
    echo ""
    echo "⏰ 检测到cron任务"
    read -p "是否删除cron任务? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        crontab -l | grep -v "CTV_Monitor" | crontab -
        echo "✅ cron任务已删除"
    fi
else
    echo "ℹ️  未检测到cron任务"
fi

echo ""
echo "📊 你仍可以手动运行:"
echo "   cd /Users/zhuxiaolin/CTV_Monitor"
echo "   python3 monitor.py"
