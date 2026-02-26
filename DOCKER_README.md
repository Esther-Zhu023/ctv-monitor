# CTV监控系统 - Docker部署版本

适用于任何支持Docker的平台进行定时运行。

## 🚀 快速开始

### 方法1: Docker Compose（推荐）

```bash
# 构建并启动（每天9:00自动运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 方法2: Docker命令

```bash
# 构建镜像
docker build -t ctv-monitor:latest .

# 单次运行
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  ctv-monitor:latest

# 查看报告
cat reports/latest_report.json
```

## 🔄 集成到自动化平台

### GitHub Actions
```yaml
# .github/workflows/ctv-monitor.yml
name: CTV Monitor
on:
  schedule:
    - cron: '0 1 * * *'  # 每天9:00 (UTC+8 = UTC+1)
  workflow_dispatch:      # 手动触发

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run CTV Monitor
        run: |
          docker build -t ctv-monitor .
          docker run --rm \
            -v ${{ github.workspace }}/reports:/app/reports \
            ctv-monitor
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: ctv-reports
          path: reports/
```

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - monitor

ctv_monitor:
  stage: monitor
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t ctv-monitor .
    - docker run --rm -v $CI_PROJECT_DIR/reports:/app/reports ctv-monitor
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
  only:
    - schedules
```

### Kubernetes CronJob
```yaml
# k8s-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ctv-monitor
spec:
  schedule: "0 9 * * *"  # 每天9:00
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: ctv-monitor
            image: ctv-monitor:latest
            volumeMounts:
            - name: reports
              mountPath: /app/reports
          volumes:
          - name: reports
            persistentVolumeClaim:
              claimName: ctv-reports-pvc
          restartPolicy: OnFailure
```

### AWS Lambda (定时)
```python
# lambda_function.py
import json
import subprocess
from datetime import datetime

def lambda_handler(event, context):
    # 运行监控
    result = subprocess.run(['python3', 'monitor.py'],
                          capture_output=True,
                          text=True)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'CTV monitor completed',
            'timestamp': datetime.now().isoformat(),
            'output': result.stdout
        })
    }
```

## 🔧 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TZ` | `Asia/Shanghai` | 时区 |
| `CHECK_INTERVAL_HOURS` | `24` | 检查间隔 |
| `NEWS_API_KEY` | - | NewsAPI密钥（可选） |

## 📊 持久化

报告和日志通过Docker volumes持久化：
- `./reports` → `/app/reports`
- `./logs` → `/app/logs`

## 🎯 支持的平台

任何支持Docker的平台：
- ✅ GitHub Actions
- ✅ GitLab CI
- ✅ Kubernetes
- ✅ AWS ECS/Lambda
- ✅ Google Cloud Run
- ✅ Azure Container Instances
- ✅ 各种服务器（VPS、云主机）

## 📝 自定义调度

编辑 `docker-compose.yml` 中的cron表达式：
```bash
# 每天9:00
0 9 * * *

# 每6小时
0 */6 * * *

# 每周一9:00
0 9 * * 1
```

---

**Docker Hub发布**（可选）:
```bash
docker tag ctv-monitor:latest your-username/ctv-monitor:latest
docker push your-username/ctv-monitor:latest
```
