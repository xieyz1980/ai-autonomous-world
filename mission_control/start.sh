#!/bin/bash
# Mission Control 启动脚本

echo "🚀 Starting AI Kingdom Mission Control..."

# 检查Python
echo "📋 Checking Python..."
python3 --version || exit 1

# 安装依赖
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -q

# 创建数据目录
mkdir -p /opt/ai-world/data
mkdir -p /opt/ai-world/logs

# 启动应用
echo "🌐 Starting web server on port 8085..."
python3 app.py &

PID=$!
echo $PID > /tmp/mission_control.pid

echo "✅ Mission Control started!"
echo "📊 Access: http://localhost:8085"
echo "📝 PID: $PID"
echo ""
echo "To stop: kill $PID"
