"""
启动 Flask 服务器脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import create_app
from utils.config import Config
from utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger('server')
    
    # 加载配置
    config = Config()
    
    # 验证配置
    if not config.validate():
        logger.warning("配置验证失败，某些功能可能无法使用")
    
    logger.info("=" * 50)
    logger.info("启动心血管疾病预测系统服务器")
    logger.info("=" * 50)
    logger.info(f"主机: {config.FLASK_HOST}")
    logger.info(f"端口: {config.FLASK_PORT}")
    logger.info(f"调试模式: {config.FLASK_DEBUG}")
    logger.info("=" * 50)
    
    # 创建应用
    app = create_app()
    
    # 启动服务器
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()

