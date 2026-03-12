#!/bin/bash
# AI Kingdom - 一键启动脚本
# 只需运行这个文件，全自动启动 Mission Control

set -e  # 遇到错误立即退出

echo "═══════════════════════════════════════════════════════════════"
echo "           🤖 AI Kingdom Mission Control 一键启动"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}⚠️  未在项目目录，尝试进入...${NC}"
    if [ -d "/opt/ai-world" ]; then
        cd /opt/ai-world
        echo -e "${GREEN}✅ 已进入 /opt/ai-world${NC}"
    else
        echo -e "${RED}❌ 错误: 找不到项目目录 /opt/ai-world${NC}"
        echo "请先克隆仓库: git clone https://github.com/xieyz1980/ai-autonomous-world.git /opt/ai-world"
        exit 1
    fi
fi

echo "📍 当前目录: $(pwd)"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Docker未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker安装完成，请重新登录后重试${NC}"
    exit 0
fi

# 检查docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 docker-compose未安装，正在安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ docker-compose安装完成${NC}"
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"
echo ""

# 检查端口
if lsof -Pi :8085 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口8085被占用，尝试停止旧进程...${NC}"
    docker-compose stop mission-control 2>/dev/null || true
    sleep 2
fi

# 创建必要目录
echo "📁 创建数据目录..."
mkdir -p /opt/ai-world/logs
mkdir -p /opt/ai-world/data
mkdir -p /opt/ai-world/shared

echo -e "${GREEN}✅ 目录创建完成${NC}"
echo ""

# 拉取最新代码
echo "🔄 拉取最新代码..."
git pull origin master || echo "跳过代码更新"
echo ""

# 构建并启动 Mission Control
echo "🚀 启动 Mission Control..."
docker-compose build mission-control
docker-compose up -d mission-control

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务状态
if docker ps | grep -q "ai-world-mission-control"; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           ✅ Mission Control 启动成功！${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "📊 访问地址:"
    echo "   • 本地: http://localhost:8085"
    echo "   • 公网: http://74.226.96.24:8085"
    echo ""
    echo "📋 常用命令:"
    echo "   查看日志: docker-compose logs -f mission-control"
    echo "   停止服务: docker-compose stop mission-control"
    echo "   重启服务: docker-compose restart mission-control"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}❌ 启动失败，查看日志:${NC}"
    docker-compose logs mission-control
    exit 1
fi
