"""
音频处理模块
包含DeepSeek文本生成和CosyVoice语音合成
"""

from .deepseek_client import DeepSeekClient
from .cosyvoice_client import CosyVoiceClient

__all__ = ['DeepSeekClient', 'CosyVoiceClient']
