#!/bin/bash
# AI Autonomous World - Deployment Script
# AI自主世界 - 部署脚本

set -e

echo "========================================"
echo "  AI Autonomous World Deployment"
echo "========================================"
echo ""

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

# 检查依赖
check_dependencies() {
    log_info "Checking dependencies..."
    
    command -v docker >/dev/null 2>&1 || { log_error "Docker is required but not installed."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { log_error "Docker Compose is required but not installed."; exit 1; }
    
    log_success "All dependencies satisfied"
}

# 检查环境变量
check_env() {
    log_info "Checking environment variables..."
    
    if [ ! -f .env ]; then
        log_warning ".env file not found, creating from template..."
        cp .env.example .env
        log_warning "Please edit .env file and add your API keys"
        exit 1
    fi
    
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
        log_error "OPENAI_API_KEY is not set in .env file"
        exit 1
    fi
    
    log_success "Environment variables configured"
}

# 创建目录结构
setup_directories() {
    log_info "Setting up directory structure..."
    
    mkdir -p shared/memory
    mkdir -p logs
    mkdir -p config/grafana
    
    chmod 777 shared logs
    
    log_success "Directories created"
}

# 构建镜像
build_images() {
    log_info "Building Docker images..."
    
    docker-compose build
    
    log_success "Images built successfully"
}

# 启动系统
start_system() {
    log_info "Starting AI World..."
    
    docker-compose up -d
    
    log_success "AI World started"
}

# 等待服务就绪
wait_for_ready() {
    log_info "Waiting for services to be ready..."
    
    for i in {1..30}; do
        if curl -s http://localhost:8080/health >/dev/null 2>&1; then
            log_success "AI World is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    
    log_error "Timeout waiting for services"
    return 1
}

# 显示状态
show_status() {
    echo ""
    echo "========================================"
    echo "  AI World Status"
    echo "========================================"
    echo ""
    
    echo "Services:"
    docker-compose ps
    
    echo ""
    echo "Endpoints:"
    echo "  - Message Bus API: http://localhost:8080"
    echo "  - Health Check:    http://localhost:8080/health"
    echo "  - Nodes List:      http://localhost:8080/nodes"
    echo ""
    
    echo "Logs:"
    echo "  docker-compose logs -f"
    echo ""
    
    echo "Stop:"
    echo "  docker-compose down"
    echo ""
}

# 主函数
main() {
    case "${1:-deploy}" in
        deploy)
            check_dependencies
            check_env
            setup_directories
            build_images
            start_system
            wait_for_ready
            show_status
            ;;
        stop)
            log_info "Stopping AI World..."
            docker-compose down
            log_success "AI World stopped"
            ;;
        restart)
            log_info "Restarting AI World..."
            docker-compose restart
            wait_for_ready
            show_status
            ;;
        logs)
            docker-compose logs -f
            ;;
        status)
            docker-compose ps
            ;;
        update)
            log_info "Updating AI World..."
            docker-compose pull
            docker-compose build
            docker-compose up -d
            log_success "AI World updated"
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|logs|status|update}"
            exit 1
            ;;
    esac
}

main "$@"
