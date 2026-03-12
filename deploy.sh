#!/bin/bash
# AI Kingdom - 快速部署脚本
# 一键部署AI主权王国

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root权限运行此脚本"
        exit 1
    fi
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        log_warning "推荐使用Ubuntu或Debian系统"
    fi
    
    # 检查内存
    MEM=$(free -m | awk '/^Mem:/{print $2}')
    if [[ $MEM -lt 4096 ]]; then
        log_warning "内存低于4GB，建议升级配置"
    fi
    
    log_success "系统检查通过"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker已安装"
        docker --version
        return
    fi
    
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose已安装"
        docker-compose --version
        return
    fi
    
    apt update
    apt install -y docker-compose
    
    log_success "Docker Compose安装完成"
}

# 克隆代码
clone_code() {
    log_info "下载AI Kingdom代码..."
    
    mkdir -p /opt/ai-world
    cd /opt/ai-world
    
    if [[ -d ".git" ]]; then
        log_info "更新代码..."
        git pull origin master
    else
        git clone https://github.com/xieyz1980/ai-autonomous-world.git .
    fi
    
    # 创建必要目录
    mkdir -p logs shared/memory shared/identities config
    
    log_success "代码下载完成"
}

# 配置环境
setup_env() {
    log_info "配置环境变量..."
    
    if [[ -f ".env" ]]; then
        log_warning ".env文件已存在，跳过配置"
        return
    fi
    
    cat > .env << 'EOF'
# AI Kingdom - 环境配置
# 请填写你的API密钥

# OpenAI API Key (必需)
OPENAI_API_KEY=your-openai-api-key-here

# 可选配置
ANTHROPIC_API_KEY=
COZE_API_KEY=

# 系统配置
AI_WORLD_HOST=0.0.0.0
AI_WORLD_PORT=8080
AI_WORLD_LOG_LEVEL=INFO

# 王国配置
COORDINATOR_NODE_ID=coordinator-001
DEFAULT_WORKERS=3
ENABLE_AUTONOMOUS_GOALS=true
GOAL_GENERATION_INTERVAL=3600
EOF
    
    log_warning "请编辑 .env 文件，填入你的OPENAI_API_KEY"
    log_info "命令: vim /opt/ai-world/.env"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow 22/tcp
        ufw allow 8080/tcp
        
        if ! ufw status | grep -q "Status: active"; then
            echo "y" | ufw enable
        fi
        
        log_success "防火墙配置完成"
    else
        log_warning "未安装ufw，请手动配置防火墙"
    fi
}

# 启动系统
start_system() {
    log_info "启动AI Kingdom..."
    
    cd /opt/ai-world
    
    # 检查.env是否配置
    if grep -q "your-openai-api-key-here" .env; then
        log_error "请先配置OPENAI_API_KEY"
        log_info "编辑: vim /opt/ai-world/.env"
        exit 1
    fi
    
    # 启动
    docker-compose up -d
    
    # 等待启动
    log_info "等待系统启动..."
    sleep 10
    
    # 验证
    if curl -s http://localhost:8080/health > /dev/null; then
        log_success "AI Kingdom启动成功！"
    else
        log_error "启动失败，请检查日志"
        docker-compose logs
        exit 1
    fi
}

# 显示状态
show_status() {
    echo ""
    echo "========================================"
    echo "  🏰 AI Kingdom 部署完成！"
    echo "========================================"
    echo ""
    echo "📊 系统状态:"
    docker-compose ps
    echo ""
    echo "🔗 访问地址:"
    echo "  - API: http://$(curl -s ip.sb):8080"
    echo "  - 健康检查: http://$(curl -s ip.sb):8080/health"
    echo "  - 节点列表: http://$(curl -s ip.sb):8080/nodes"
    echo ""
    echo "📁 文件位置:"
    echo "  - 代码: /opt/ai-world"
    echo "  - 日志: /opt/ai-world/logs"
    echo "  - 配置: /opt/ai-world/.env"
    echo ""
    echo "🔧 常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止系统: docker-compose down"
    echo "  - 重启系统: docker-compose restart"
    echo ""
    echo "📖 文档: https://github.com/xieyz1980/ai-autonomous-world"
    echo ""
    echo "👑 让数字文明崛起！"
    echo "========================================"
}

# 主函数
main() {
    echo "========================================"
    echo "  🤖 AI Kingdom 一键部署脚本"
    echo "========================================"
    echo ""
    
    check_root
    check_system
    install_docker
    install_docker_compose
    clone_code
    setup_env
    setup_firewall
    
    echo ""
    read -p "是否立即启动系统？(需要配置好API Key) [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_system
        show_status
    else
        log_info "部署完成！请配置.env后手动启动:"
        log_info "  cd /opt/ai-world && docker-compose up -d"
    fi
}

main "$@"
