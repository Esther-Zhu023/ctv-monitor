#!/bin/bash
# 一键部署脚本 - 支持多平台

echo "🚀 CTV监控系统 - 一键部署"
echo "========================"
echo ""

# 检查是否在正确的目录
if [ ! -f "monitor.py" ]; then
    echo "❌ 错误: 请在CTV_Monitor目录下运行此脚本"
    exit 1
fi

echo "请选择部署平台:"
echo ""
echo "1. GitHub Actions  (推荐，免费)"
echo "2. Docker Compose  (本地或服务器)"
echo "3. Docker 单次运行"
echo "4. GitLab CI"
echo "5. API服务器模式  (HTTP触发)"
echo "6. 本地macOS定时任务"
echo ""
read -p "输入选项 (1-6): " platform

case $platform in
    1)
        echo ""
        echo "📱 部署到 GitHub Actions"
        echo "----------------------"

        # 检查git
        if ! command -v git &> /dev/null; then
            echo "❌ 需要安装git"
            exit 1
        fi

        # 检查gh CLI
        if ! command -v gh &> /dev/null; then
            echo "⚠️  未安装GitHub CLI，正在安装..."
            brew install gh || {
                echo "请手动安装: https://cli.github.com/"
                exit 1
            }
        fi

        # 初始化git
        if [ ! -d ".git" ]; then
            git init
            git add .
            git commit -m "Initial: CTV Monitor"
        fi

        # 创建仓库
        echo "创建GitHub仓库..."
        gh repo create ctv-monitor --public --source=. --remote=origin --push

        echo ""
        echo "✅ 部署成功！"
        echo ""
        echo "下一步:"
        echo "1. 访问: https://github.com/$(git config get github.user)/ctv-monitor/actions"
        echo "2. 启用GitHub Actions"
        echo "3. 查看 .github/workflows/ctv-monitor.yml 修改运行时间"
        echo "4. 手动触发: gh workflow run ctv-monitor.yml"
        ;;

    2)
        echo ""
        echo "🐳 部署到 Docker Compose"
        echo "-----------------------"

        # 检查docker
        if ! command -v docker &> /dev/null; then
            echo "❌ 需要安装Docker"
            exit 1
        fi

        # 构建并启动
        docker-compose up -d

        echo ""
        echo "✅ Docker定时任务已启动（每天9:00）"
        echo ""
        echo "管理命令:"
        echo "  查看日志: docker-compose logs -f"
        echo "  停止: docker-compose down"
        echo "  重启: docker-compose restart"
        ;;

    3)
        echo ""
        echo "🐳 Docker 单次运行"
        echo "-----------------"

        if ! command -v docker &> /dev/null; then
            echo "❌ 需要安装Docker"
            exit 1
        fi

        echo "构建镜像..."
        docker build -t ctv-monitor .

        echo "运行监控..."
        docker run --rm \
            -v "$(pwd)/reports:/app/reports" \
            -v "$(pwd)/logs:/app/logs" \
            ctv-monitor

        echo ""
        echo "✅ 运行完成"
        echo "查看报告: cat reports/latest_report.json"
        ;;

    4)
        echo ""
        echo "🦊 部署到 GitLab CI"
        echo "------------------"

        if [ ! -f ".gitlab-ci.yml" ]; then
            cat > .gitlab-ci.yml << 'EOF'
stages:
  - monitor

ctv_monitor:
  stage: monitor
  image: python:3.11
  script:
    - pip install feedparser requests python-dateutil beautifulsoup4
    - mkdir -p logs reports
    - python3 monitor.py
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
  only:
    - schedules
EOF
        fi

        echo "✅ .gitlab-ci.yml 已创建"
        echo ""
        echo "下一步:"
        echo "1. 推送到GitLab"
        echo "2. 进入项目 → CI/CD → Schedules"
        echo "3. 创建新的定时任务"
        ;;

    5)
        echo ""
        echo "🌐 API服务器模式"
        echo "---------------"

        if ! command -v docker &> /dev/null; then
            echo "❌ 需要安装Docker"
            exit 1
        fi

        echo "构建API镜像..."
        docker build -f Dockerfile.api -t ctv-monitor-api .

        echo "启动API服务器..."
        docker run -d \
            -p 8080:8080 \
            -v "$(pwd)/reports:/app/reports" \
            -v "$(pwd)/logs:/app/logs" \
            --name ctv-api \
            ctv-monitor-api

        echo ""
        echo "✅ API服务器已启动"
        echo ""
        echo "API端点:"
        echo "  健康检查: curl http://localhost:8080/health"
        echo "  运行监控: curl http://localhost:8080/run"
        echo "  获取报告: curl http://localhost:8080/report"
        echo "  系统状态: curl http://localhost:8080/status"
        echo ""
        echo "管理命令:"
        echo "  查看日志: docker logs -f ctv-api"
        echo "  停止服务: docker stop ctv-api && docker rm ctv-api"
        ;;

    6)
        echo ""
        echo "🍎 macOS本地定时任务"
        echo "-------------------"

        bash start.sh
        ;;

    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "📚 更多信息: cat PLATFORM_INTEGRATION.md"
