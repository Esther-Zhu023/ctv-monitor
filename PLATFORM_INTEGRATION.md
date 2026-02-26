# CTV监控系统 - 多平台集成指南

## 🚀 快速开始

### 选择你的平台

| 平台 | 难度 | 说明 |
|------|------|------|
| **GitHub Actions** | ⭐ 简单 | 免费推荐，支持cron |
| **Docker** | ⭐⭐ 中等 | 通用性强 |
| **GitLab CI** | ⭐ 简单 | 类似GitHub Actions |
| **Kubernetes** | ⭐⭐⭐ 复杂 | 企业级 |
| **AWS Lambda** | ⭐⭐ 中等 | 云原生 |

---

## 1️⃣ GitHub Actions（推荐）

### 设置步骤

```bash
# 1. 初始化Git仓库
git init
git add .
git commit -m "Initial: CTV Monitor"

# 2. 创建GitHub仓库
gh repo create ctv-monitor --public --source=.
git push -u origin main
```

### 配置定时任务

编辑 `.github/workflows/ctv-monitor.yml`:

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC时间，换算成北京时间-7小时
  # 例如：北京时间9:00 = UTC 1:00
```

### 常用cron表达式

| 北京时间 | UTC Cron |
|---------|----------|
| 每天 9:00 | `0 1 * * *` |
| 每天 0:00 | `0 16 * * *` (前一天) |
| 每6小时 | `0 */6 * * *` |
| 每周一 9:00 | `0 1 * * 1` |

### 管理任务

```bash
# 查看运行历史
gh run list --repo=$(git remote get-url origin | sed 's/.*:\\/\\///' | sed 's/\\.git//')

# 手动触发
gh workflow run ctv-monitor.yml --repo=$(git remote get-url origin | sed 's/.*:\\/\\///' | sed 's/\\.git//')

# 查看最新运行
gh run view --repo=$(git remote get-url origin | sed 's/.*:\\/\\///' | sed 's/\\.git//')

# 下载报告
gh run download --name ctv-report-* --repo=$(git remote get-url origin | sed 's/.*:\\/\\///' | sed 's/\\.git//')
```

---

## 2️⃣ Docker版本

### 本地运行

```bash
# 构建镜像
docker build -t ctv-monitor .

# 运行
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  ctv-monitor
```

### Docker Compose（定时）

```bash
# 启动（每天9:00运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### API服务器模式

```bash
# 构建API版本
docker build -f Dockerfile.api -t ctv-monitor-api .

# 运行API服务器
docker run -d -p 8080:8080 \
  -v $(pwd)/reports:/app/reports \
  --name ctv-api \
  ctv-monitor-api

# 手动触发
curl http://localhost:8080/run

# 获取报告
curl http://localhost:8080/report

# 健康检查
curl http://localhost:8080/health
```

---

## 3️⃣ GitLab CI

### 配置文件

创建 `.gitlab-ci.yml`:

```yaml
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
```

### 设置定时任务

1. 进入项目 → CI/CD → Schedules
2. 点击 "New schedule"
3. 设置cron表达式和时区
4. 选择目标分支

---

## 4️⃣ Kubernetes CronJob

```bash
# 应用配置
kubectl apply -f k8s-cronjob.yaml

# 查看CronJobs
kubectl get cronjobs

# 查看执行历史
kubectl get jobs

# 查看日志
kubectl logs -l job-name=ctv-monitor-*

# 手动触发
kubectl create job --from=cronjob/ctv-monitor manual-run-$(date +%s)
```

---

## 5️⃣ AWS Lambda

### 部署步骤

```bash
# 安装AWS CLI
pip install awscli

# 创建Lambda函数
aws lambda create-function \
  --function-name ctv-monitor \
  --runtime python3.11 \
  --role $LAMBDA_ROLE_ARN \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment-package.zip

# 添加EventBridge规则（每天9:00）
aws events put-rule \
  --name ctv-monitor-schedule \
  --schedule-expression 'cron(0 1 * * ? *)'

# 添加目标
aws events put-targets \
  --rule ctv-monitor-schedule \
  --targets "Id"="1","Arn"="$LAMBDA_ARN"
```

---

## 6️⃣ Make.com / Zapier集成

### Webhook方式

```python
# 在你的服务器上运行API服务器
docker run -d -p 8080:8080 ctv-monitor-api

# Make.com中设置HTTP webhook
# URL: https://your-server.com/run
# Method: POST
```

---

## 📊 监控运行状态

### GitHub Actions
- 查看Actions标签页
- 每次运行都会生成报告artifact
- 支持邮件通知

### Docker
```bash
docker-compose logs -f
docker ps
```

### API模式
```bash
curl http://localhost:8080/status
```

---

## 🔧 修改运行时间

### GitHub Actions
编辑 `.github/workflows/ctv-monitor.yml`:
```yaml
schedule:
  - cron: '0 1 * * *'  # 修改这里
```

### Docker Compose
编辑 `docker-compose.yml`:
```yaml
command: >
  sh -c "echo '0 9 * * * cd /app && python3 monitor.py' > /etc/crontabs/root && cron -f"
```

---

## 📦 发布到Docker Hub

```bash
# 登录
docker login

# 打标签
docker tag ctv-monitor:latest your-username/ctv-monitor:latest

# 推送
docker push your-username/ctv-monitor:latest

# 其他平台使用
docker run --rm your-username/ctv-monitor:latest
```

---

## 🎯 推荐方案对比

| 需求 | 推荐方案 | 原因 |
|------|---------|------|
| 个人使用 | GitHub Actions | 免费、简单、可靠 |
| 企业内部 | GitLab CI | 私有部署、安全 |
| 云原生 | Kubernetes | 可扩展、企业级 |
| 灵活触发 | API服务器 | HTTP调用、适合集成 |
| 离线环境 | Docker Compose | 自包含、无依赖 |

---

## ❓ 常见问题

### Q: GitHub Actions cron不工作？
A: 默认是UTC时间，需要减7小时（北京时间）

### Q: Docker容器无法访问网络？
A: 检查防火墙和网络配置

### Q: 如何修改监控的公司列表？
A: 编辑 `known_entities.json` 后提交

### Q: 如何添加邮件通知？
A: 在GitHub Actions中添加邮件步骤，或使用API服务器

---

**下一步**: 选择一个平台，按照对应步骤操作即可！
