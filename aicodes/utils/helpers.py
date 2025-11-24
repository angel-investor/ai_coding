"""
辅助函数
通用的工具函数
"""

import os
import json
from datetime import datetime
from typing import Any, Dict


def ensure_dir(directory: str):
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def load_json(file_path: str) -> Dict:
    """
    加载 JSON 文件
    
    Args:
        file_path: JSON 文件路径
        
    Returns:
        JSON 数据字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 JSON 失败: {e}")
        return {}


def save_json(data: Dict, file_path: str):
    """
    保存数据到 JSON 文件
    
    Args:
        data: 要保存的数据
        file_path: 保存路径
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存 JSON 失败: {e}")


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    获取当前时间戳字符串
    
    Args:
        format: 时间格式
        
    Returns:
        时间戳字符串
    """
    return datetime.now().strftime(format)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_input_data(data: Dict, required_fields: list) -> tuple:
    """
    验证输入数据
    
    Args:
        data: 输入数据字典
        required_fields: 必需字段列表
        
    Returns:
        (是否有效, 错误消息)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    return True, ""


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        a: 被除数
        b: 除数
        default: 除零时的默认值
        
    Returns:
        除法结果
    """
    try:
        return a / b if b != 0 else default
    except:
        return default


if __name__ == "__main__":
    # 测试辅助函数
    print(f"时间戳: {get_timestamp()}")
    print(f"文件大小: {format_file_size(1024 * 1024 * 5)}")
    
    # 测试数据验证
    test_data = {"name": "test", "age": 25}
    valid, msg = validate_input_data(test_data, ["name", "age", "email"])
    print(f"验证结果: {valid}, {msg}")

