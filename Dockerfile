FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制文件
COPY known_entities.json .
COPY monitor.py .
COPY news_fetcher.py .
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建日志和报告目录
RUN mkdir -p /app/logs /app/reports

# 设置环境变量
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

# 默认命令
CMD ["python3", "monitor.py"]
