# AI Autonomous World - Docker Image
# AI自主世界 - Docker镜像

FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /opt/ai-world

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY core/ ./core/
COPY nodes/ ./nodes/
COPY main.py .
COPY run_worker.py .

# 创建必要目录
RUN mkdir -p /opt/ai-world/shared/memory /opt/ai-world/logs /opt/ai-world/config

# 暴露端口
EXPOSE 8080 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 默认命令
CMD ["python", "main.py"]
