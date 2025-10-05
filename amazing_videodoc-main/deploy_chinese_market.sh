#!/bin/bash

# FrameNote 中国市场定制化部署脚本
# 用于快速部署包含中国化功能的视频AI总结平台

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查必要的命令
    check_command "python3"
    check_command "pip"
    check_command "git"
    
    # 检查Python版本
    python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    # 检查是否有.env文件
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，将从 .env.example 复制"
        cp .env.example .env
        log_warning "请编辑 .env 文件配置必要的环境变量"
    fi
    
    log_success "环境检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装额外的中国化功能依赖
    pip install cryptography  # RSA签名
    pip install alipay-sdk-python  # 支付宝SDK
    pip install wechatpy  # 微信SDK
    pip install alibabacloud-dysmsapi20170525  # 阿里云短信
    
    log_success "依赖安装完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 检查是否配置了数据库URL
    if grep -q "DATABASE_URL=postgresql" .env; then
        log_info "检测到PostgreSQL配置，执行数据库初始化..."
        
        # 检查psql命令
        if command -v psql &> /dev/null; then
            # 从.env文件读取数据库配置
            source .env
            
            # 执行初始化脚本
            if [ -f "database/init_chinese_market.sql" ]; then
                psql $DATABASE_URL -f database/init_chinese_market.sql
                log_success "数据库初始化完成"
            else
                log_warning "数据库初始化脚本不存在，跳过数据库初始化"
            fi
        else
            log_warning "psql命令未找到，请手动执行数据库初始化脚本"
            log_info "脚本位置: database/init_chinese_market.sql"
        fi
    else
        log_info "未配置PostgreSQL，跳过数据库初始化"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p storage/uploads
    mkdir -p storage/processed
    mkdir -p storage/exports
    mkdir -p storage/temp
    mkdir -p logs
    
    # 设置目录权限
    chmod 755 storage
    chmod 755 storage/*
    chmod 755 logs
    
    log_success "目录创建完成"
}

# 生成密钥
generate_secrets() {
    log_info "检查密钥配置..."
    
    # 检查JWT密钥
    if grep -q "JWT_SECRET_KEY=your_jwt_secret_key_here" .env; then
        log_warning "检测到默认JWT密钥，正在生成新密钥..."
        new_jwt_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        sed -i "s/JWT_SECRET_KEY=your_jwt_secret_key_here/JWT_SECRET_KEY=$new_jwt_key/" .env
        log_success "JWT密钥已更新"
    fi
    
    log_info "请确保在.env文件中配置以下密钥："
    log_info "- 微信登录: WECHAT_APP_ID, WECHAT_APP_SECRET"
    log_info "- QQ登录: QQ_APP_ID, QQ_APP_KEY"
    log_info "- 支付宝: ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY, ALIPAY_PUBLIC_KEY"
    log_info "- 微信支付: WECHAT_PAY_MCH_ID, WECHAT_PAY_API_KEY"
    log_info "- 短信服务: SMS_ACCESS_KEY_ID, SMS_ACCESS_KEY_SECRET"
}

# 测试配置
test_configuration() {
    log_info "测试基础配置..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 测试导入
    python3 -c "
import sys
sys.path.append('.')

try:
    from models.user_models import UserRole, UserResponse
    from models.payment_models import PaymentProvider, MembershipPlan
    from models.community_models import WechatGroup, GroupType
    from services.auth_service import AuthService
    from services.payment_service import PaymentService
    from services.community_service import CommunityService
    print('✅ 所有模块导入成功')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "配置测试通过"
    else
        log_error "配置测试失败"
        exit 1
    fi
}

# 启动服务
start_service() {
    log_info "启动FrameNote服务..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查端口是否被占用
    port=$(grep "SERVER_PORT=" .env | cut -d'=' -f2)
    if [ -z "$port" ]; then
        port=8001
    fi
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        log_warning "端口 $port 已被占用，请检查是否有其他服务在运行"
        log_info "可以使用以下命令查看占用进程: lsof -i :$port"
        read -p "是否继续启动？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "在端口 $port 启动服务..."
    log_info "API文档地址: http://localhost:$port/docs"
    log_info "健康检查: http://localhost:$port/api/health"
    
    # 启动服务
    python3 main.py
}

# 显示帮助信息
show_help() {
    echo "FrameNote 中国市场定制化部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  install     - 完整安装（检查环境、安装依赖、初始化数据库）"
    echo "  start       - 启动服务"
    echo "  test        - 测试配置"
    echo "  help        - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 install  # 完整安装"
    echo "  $0 start    # 启动服务"
    echo "  $0 test     # 测试配置"
}

# 完整安装流程
full_install() {
    log_info "开始FrameNote中国市场定制化部署..."
    echo ""
    
    check_environment
    echo ""
    
    install_dependencies
    echo ""
    
    create_directories
    echo ""
    
    generate_secrets
    echo ""
    
    init_database
    echo ""
    
    test_configuration
    echo ""
    
    log_success "🎉 部署完成！"
    echo ""
    log_info "接下来的步骤："
    log_info "1. 编辑 .env 文件，配置必要的API密钥"
    log_info "2. 运行 $0 start 启动服务"
    log_info "3. 访问 http://localhost:8001/docs 查看API文档"
    echo ""
    log_info "详细配置指南请参考: CHINESE_MARKET_SETUP.md"
}

# 主函数
main() {
    case "${1:-install}" in
        "install")
            full_install
            ;;
        "start")
            start_service
            ;;
        "test")
            test_configuration
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
