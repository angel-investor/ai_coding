"""
启动 Flask 服务器脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import create_app
from utils.config import Config


def main():
    """主函数"""
    print("=" * 60)
    print("启动心血管疾病预测 API 服务器")
    print("=" * 60)
    
    # 加载配置
    config = Config()
    
    # 验证配置
    if not config.validate():
        print("\n配置验证失败，请检查 .env 文件")
        sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    print(f"\n服务器配置:")
    print(f"  地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"  调试模式: {config.FLASK_DEBUG}")
    print(f"\nAPI 端点:")
    print(f"  预测接口: http://localhost:{config.FLASK_PORT}/api/predict")
    print(f"  问答接口: http://localhost:{config.FLASK_PORT}/api/chat")
    print(f"  语音接口: http://localhost:{config.FLASK_PORT}/api/voice")
    print(f"  模型信息: http://localhost:{config.FLASK_PORT}/api/model/info")
    print(f"\n前端页面:")
    print(f"  http://localhost:{config.FLASK_PORT}/web/index.html")
    print("\n" + "=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    # 启动服务器
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == "__main__":
    main()

