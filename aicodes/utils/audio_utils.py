"""
音频工具类
处理音频文件保存、路径管理等
"""

import os
import uuid
from typing import Optional


def ensure_audio_directory(base_dir: str = 'static/audio') -> str:
    """
    确保音频目录存在
    
    Args:
        base_dir: 基础目录路径
        
    Returns:
        str: 音频目录的完整路径
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audio_dir = os.path.join(project_root, base_dir)
    
    # 创建目录（如果不存在）
    os.makedirs(audio_dir, exist_ok=True)
    
    return audio_dir


def generate_audio_filename(extension: str = 'wav') -> str:
    """
    生成唯一的音频文件名
    
    Args:
        extension: 文件扩展名
        
    Returns:
        str: 文件名（不含路径）
    """
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{extension}"


def save_audio_file(audio_data: bytes, filename: Optional[str] = None) -> tuple:
    """
    保存音频文件
    
    Args:
        audio_data: 音频二进制数据
        filename: 文件名（可选，不提供则自动生成）
        
    Returns:
        tuple: (完整文件路径, URL路径)
    """
    # 确保目录存在
    audio_dir = ensure_audio_directory()
    
    # 生成文件名
    if filename is None:
        filename = generate_audio_filename()
    
    # 完整文件路径
    file_path = os.path.join(audio_dir, filename)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    
    # 生成 URL 路径
    audio_url = f"/static/audio/{filename}"
    
    return file_path, audio_url


def get_audio_url(filename: str) -> str:
    """
    根据文件名生成 URL
    
    Args:
        filename: 文件名
        
    Returns:
        str: URL 路径
    """
    return f"/static/audio/{filename}"


def delete_audio_file(filename: str) -> bool:
    """
    删除音频文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否成功删除
    """
    try:
        audio_dir = ensure_audio_directory()
        file_path = os.path.join(audio_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def cleanup_old_audio_files(max_files: int = 100):
    """
    清理旧的音频文件（保留最新的 N 个）
    
    Args:
        max_files: 保留的最大文件数
    """
    try:
        audio_dir = ensure_audio_directory()
        
        # 获取所有音频文件
        files = []
        for filename in os.listdir(audio_dir):
            if filename.endswith('.wav') or filename.endswith('.mp3'):
                file_path = os.path.join(audio_dir, filename)
                files.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序
        files.sort(key=lambda x: x[1], reverse=True)
        
        # 删除多余的文件
        for file_path, _ in files[max_files:]:
            try:
                os.remove(file_path)
            except Exception:
                pass
                
    except Exception:
        pass

