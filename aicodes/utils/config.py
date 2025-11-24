"""
配置管理
从环境变量和.env文件加载配置
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """配置类"""
    
    def __init__(self, env_file: str = '.env'):
        """
        初始化配置
        
        Args:
            env_file: .env文件路径
        """
        # 加载.env文件
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # DeepSeek配置
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
        self.DEEPSEEK_API_URL = os.getenv(
            'DEEPSEEK_API_URL', 
            'https://api.deepseek.com/v1'
        )
        
        # 模型配置
        self.MODEL_PATH = os.getenv('MODEL_PATH', './model/xgb_model.pkl')
        self.MODEL_DIR = os.path.dirname(self.MODEL_PATH)
        
        # 数据配置
        self.DATA_PATH = os.getenv(
            'DATA_PATH', 
            'D:/project/workspace/ai_coding/data/心血管疾病.xlsx'
        )
        
        # CosyVoice配置
        self.COSYVOICE_APPKEY = os.getenv('COSYVOICE_APPKEY', '')
        self.COSYVOICE_TOKEN = os.getenv('COSYVOICE_TOKEN', '')
        self.COSYVOICE_TIMEOUT = int(os.getenv('COSYVOICE_TIMEOUT', '30'))  # 超时时间（秒）
        self.COSYVOICE_MAX_RETRIES = int(os.getenv('COSYVOICE_MAX_RETRIES', '3'))  # 最大重试次数
        
        # Flask配置
        self.FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
        self.FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
        self.FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        # 日志配置
        self.LOG_DIR = os.getenv('LOG_DIR', './logs')
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self) -> bool:
        """
        验证必需的配置项
        
        Returns:
            bool: 配置是否有效
        """
        required_fields = [
            'DEEPSEEK_API_KEY',
            'COSYVOICE_APPKEY',
            'COSYVOICE_TOKEN'
        ]
        
        missing = []
        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)
        
        if missing:
            print(f"警告: 缺少必需的配置项: {', '.join(missing)}")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"Config(\n"
            f"  DEEPSEEK_API_URL={self.DEEPSEEK_API_URL}\n"
            f"  MODEL_PATH={self.MODEL_PATH}\n"
            f"  DATA_PATH={self.DATA_PATH}\n"
            f"  FLASK_HOST={self.FLASK_HOST}\n"
            f"  FLASK_PORT={self.FLASK_PORT}\n"
            f")"
        )
