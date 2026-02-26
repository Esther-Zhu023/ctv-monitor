#!/bin/bash
# Docker版本的CTV监控启动脚本

echo "🐳 CTV监控 - Docker版本"
echo "======================"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

echo "📦 构建Docker镜像..."
docker build -t ctv-monitor:latest .

echo ""
echo "✅ 镜像构建完成"
echo ""
echo "运行选项："
echo ""
echo "1. 单次运行（立即执行）"
echo "   docker run --rm -v \$(pwd)/reports:/app/reports -v \$(pwd)/logs:/app/logs ctv-monitor:latest"
echo ""
echo "2. 定时运行（每天9:00，推荐）"
echo "   docker-compose up -d"
echo ""
echo "3. 查看日志"
echo "   docker-compose logs -f"
echo ""
echo "4. 停止定时任务"
echo "   docker-compose down"
echo ""

read -p "选择运行模式 (1/2): " mode

case $mode in
    1)
        echo ""
        echo "🚀 立即运行监控..."
        docker run --rm \
            -v "$(pwd)/reports:/app/reports" \
            -v "$(pwd)/logs:/app/logs" \
            ctv-monitor:latest
        ;;
    2)
        echo ""
        echo "⏰ 启动定时任务（每天9:00）..."
        docker-compose up -d
        echo "✅ 定时任务已启动"
        echo ""
        echo "管理命令："
        echo "  查看日志: docker-compose logs -f"
        echo "  停止任务: docker-compose down"
        echo "  重启任务: docker-compose restart"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
