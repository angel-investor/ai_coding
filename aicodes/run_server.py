"""
启动 Flask 预测服务器
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.predict_api import create_app
from utils.logger import setup_logger

# 设置日志
logger = setup_logger('server', log_dir='./logs')


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("启动心血管疾病预测服务器")
    logger.info("=" * 50)
    
    # 创建应用
    app = create_app()
    
    # 配置
    host = '0.0.0.0'
    port = 5000
    debug = False
    
    logger.info(f"主机: {host}")
    logger.info(f"端口: {port}")
    logger.info(f"调试模式: {debug}")
    logger.info("=" * 50)
    
    # 打印访问地址
    print("\n" + "=" * 60)
    print("🚀 心血管疾病预测服务器启动成功！")
    print("=" * 60)
    print("\n访问地址:")
    print(f"  📊 预测页面: http://localhost:{port}/web/predict.html")
    print(f"  🔌 API 接口: http://localhost:{port}/predict")
    print(f"  📖 API 文档: http://localhost:{port}/")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    # 启动服务器
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("服务器已停止")
        print("\n服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        print(f"\n❌ 服务器启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

