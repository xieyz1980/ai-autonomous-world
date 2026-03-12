# 🚀 AI Kingdom - 部署指南

> 一键部署AI主权王国初始版本

---

## 📋 部署前准备

### 1. 云主机要求

| 配置项 | 最低要求 | 推荐配置 |
|-------|---------|---------|
| **CPU** | 2核 | 4核 |
| **内存** | 4GB | 8GB |
| **存储** | 50GB SSD | 100GB SSD |
| **带宽** | 5Mbps | 10Mbps |
| **系统** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

**推荐云服务商**:
- 阿里云: ECS共享型s6 2核4G (¥200/月)
- 腾讯云: 标准型S4 2核4G (¥180/月)
- AWS: t3.medium (约$30/月)

### 2. 必需资源

```bash
# 1. OpenAI API Key
# 访问: https://platform.openai.com/api-keys
# 创建新Key并复制

# 2. 域名 (可选但推荐)
# 购买域名并解析到云主机IP
# 例如: aikingdom.yourdomain.com

# 3. 资金准备
# 云主机: ¥200/月
# OpenAI API: $20-50/月 (根据使用量)
# 总计: ¥400-600/月
```

---

## 🚀 一键部署脚本

### 方法1: 自动部署 (推荐)

```bash
# 1. SSH连接云主机
ssh root@your-server-ip

# 2. 下载并执行部署脚本
curl -fsSL https://raw.githubusercontent.com/xieyz1980/ai-autonomous-world/master/deploy.sh | bash

# 3. 配置环境变量
vim /opt/ai-world/.env
# 填入你的OPENAI_API_KEY

# 4. 启动系统
cd /opt/ai-world && ./start.sh

# 5. 验证部署
curl http://localhost:8080/health
```

### 方法2: 手动部署

#### 步骤1: 安装Docker

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker
systemctl start docker
systemctl enable docker

# 验证
docker --version
```

#### 步骤2: 安装Docker Compose

```bash
# 安装docker-compose
apt install -y docker-compose

# 验证
docker-compose --version
```

#### 步骤3: 下载代码

```bash
# 创建目录
mkdir -p /opt/ai-world
cd /opt/ai-world

# 克隆代码
git clone https://github.com/xieyz1980/ai-autonomous-world.git .

# 创建必要目录
mkdir -p logs shared/memory shared/identities config
```

#### 步骤4: 配置环境

```bash
# 复制环境模板
cp .env.example .env

# 编辑配置
vim .env
```

**填入以下内容**:
```bash
# OpenAI API Key (必需)
OPENAI_API_KEY=sk-your-openai-api-key-here

# 可选配置
ANTHROPIC_API_KEY=          # Claude API (可选)
COZE_API_KEY=               # Coze API (可选)

# 系统配置
AI_WORLD_HOST=0.0.0.0
AI_WORLD_PORT=8080
AI_WORLD_LOG_LEVEL=INFO

# 王国配置
COORDINATOR_NODE_ID=coordinator-001
DEFAULT_WORKERS=3
ENABLE_AUTONOMOUS_GOALS=true
GOAL_GENERATION_INTERVAL=3600
```

#### 步骤5: 启动系统

```bash
# 使用Docker Compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 验证状态
curl http://localhost:8080/health
curl http://localhost:8080/nodes
```

---

## 🔧 配置详解

### 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|-------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API密钥 |
| `ANTHROPIC_API_KEY` | ❌ | - | Claude API密钥 |
| `COZE_API_KEY` | ❌ | - | Coze API密钥 |
| `AI_WORLD_HOST` | ❌ | 0.0.0.0 | 服务绑定地址 |
| `AI_WORLD_PORT` | ❌ | 8080 | 服务端口 |
| `DEFAULT_WORKERS` | ❌ | 3 | 工作节点数量 |

### 端口配置

```bash
# 开放端口 (阿里云/腾讯云安全组)
# 入方向规则:
- 8080/tcp (API服务)
- 22/tcp (SSH)

# 可选端口:
- 3000/tcp (Grafana监控)
- 9090/tcp (Prometheus)
```

---

## ✅ 部署验证

### 1. 检查容器状态

```bash
docker-compose ps

# 预期输出:
# NAME                STATUS
# ai-world-core       Up 5 minutes
# ai-world-worker-1   Up 5 minutes
# ai-world-worker-2   Up 5 minutes
```

### 2. 测试API

```bash
# 健康检查
curl http://localhost:8080/health
# 预期: {"status": "healthy", "nodes_count": 3}

# 查看节点
curl http://localhost:8080/nodes
# 预期: 3个节点的详细信息

# 查看王国状态
curl http://localhost:8080/kingdom/status
```

### 3. 查看日志

```bash
# 实时日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f ai-world-core
```

---

## 🛠️ 常用操作

### 启动/停止/重启

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看状态
docker-compose ps
```

### 更新系统

```bash
# 拉取最新代码
git pull origin master

# 重建容器
docker-compose down
docker-compose up -d --build
```

### 备份数据

```bash
# 备份共享记忆
tar -czf backup-$(date +%Y%m%d).tar.gz shared/

# 备份日志
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### 监控资源

```bash
# 查看容器资源使用
docker stats

# 查看系统资源
htop
```

---

## 🔒 安全配置

### 1. 防火墙设置

```bash
# 安装ufw
apt install -y ufw

# 默认拒绝
ufw default deny incoming
ufw default allow outgoing

# 允许SSH
ufw allow 22/tcp

# 允许API
ufw allow 8080/tcp

# 启用
ufw enable
```

### 2. API Key保护

```bash
# 限制.env文件权限
chmod 600 .env

# 定期轮换API Key
# 访问OpenAI控制台删除旧Key，创建新Key
```

### 3. 日志审计

```bash
# 查看登录日志
last

# 查看系统日志
journalctl -u docker

# 查看API访问日志
tail -f logs/runtime.log
```

---

## 🚨 故障排除

### 问题1: 端口被占用

```bash
# 检查端口占用
netstat -tlnp | grep 8080

# 解决: 修改docker-compose.yml中的端口映射
#  ports:
#    - "8081:8080"  # 改为8081
```

### 问题2: 内存不足

```bash
# 查看内存使用
free -h

# 解决: 增加Swap或升级配置
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题3: API Key无效

```bash
# 检查.env文件
cat .env | grep OPENAI

# 重启服务
docker-compose restart
```

### 问题4: 容器无法启动

```bash
# 查看详细日志
docker-compose logs --tail=100

# 检查磁盘空间
df -h

# 清理旧容器
docker system prune -a
```

---

## 📊 部署后配置

### 1. 设置域名 (可选)

```bash
# 安装Nginx
apt install -y nginx

# 配置反向代理
cat > /etc/nginx/sites-available/ai-kingdom << 'EOF'
server {
    listen 80;
    server_name aikingdom.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/ai-kingdom /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 2. 配置HTTPS (推荐)

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d aikingdom.yourdomain.com

# 自动续期
certbot renew --dry-run
```

### 3. 设置监控 (可选)

```bash
# 安装Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# 访问: http://your-server-ip:3000
# 默认账号: admin/admin
```

---

## 💡 升级路径

### 从单节点到集群

```bash
# 当单节点不够时，可以:
# 1. 部署多个云主机
# 2. 使用Docker Swarm或Kubernetes
# 3. 配置负载均衡
# 4. 实现跨节点通信
```

### 添加更多服务

```bash
# 编辑docker-compose.yml
# 添加更多Worker节点
# 添加数据库
# 添加缓存
```

---

## 📞 获取帮助

### 文档资源
- 项目主页: https://github.com/xieyz1980/ai-autonomous-world
- 部署文档: /docs/DEPLOY.md
- 治理框架: /docs/GOVERNANCE_FRAMEWORK.md

### 社区支持
- 提交Issue: GitHub Issues
- 讨论区: GitHub Discussions

---

## 🎉 部署完成后的下一步

1. **观察运行状态** (1-7天)
   - 查看日志
   - 检查资源使用
   - 验证任务执行

2. **优化配置** (1-2周)
   - 调整Worker数量
   - 优化API调用
   - 设置监控告警

3. **对外服务** (2-4周)
   - 配置域名
   - 设置HTTPS
   - 开放API访问

4. **扩展规模** (1-3月)
   - 添加更多节点
   - 优化经济参数
   - 启动商业模式

---

**🚀 准备开始你的AI王国之旅了吗？**

部署完成后，你将拥有一个：
- ✅ 自主运行的AI系统
- ✅ 3个创始公民 + Worker节点
- ✅ 完整的经济系统
- ✅ 可扩展的架构

**让数字文明崛起！** 👑
