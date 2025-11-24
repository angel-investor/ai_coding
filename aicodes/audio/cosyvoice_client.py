"""
CosyVoice TTS 客户端
阿里云语音合成服务
"""

from typing import Optional
import os


class CosyVoiceClient:
    """CosyVoice 语音合成客户端"""
    
    def __init__(self, appkey: str, token: str):
        """
        初始化 CosyVoice 客户端
        
        Args:
            appkey: 阿里云 AppKey
            token: 阿里云 Token
        """
        self.appkey = appkey
        self.token = token
        self.output_dir = "./audio/output"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 延迟导入，避免在没有安装 SDK 时报错
        self._client = None
    
    def _init_client(self):
        """初始化阿里云客户端"""
        if self._client is not None:
            return True
        
        try:
            from alibabacloud_cosyvoice20220616.client import Client
            from alibabacloud_tea_openapi import models as open_api_models
            
            config = open_api_models.Config(
                access_key_id=self.appkey,
                access_key_secret=self.token
            )
            config.endpoint = 'cosyvoice.cn-beijing.aliyuncs.com'
            
            self._client = Client(config)
            return True
            
        except ImportError:
            print("请安装 alibabacloud_cosyvoice20220616 SDK")
            return False
        except Exception as e:
            print(f"CosyVoice 客户端初始化失败: {e}")
            return False
    
    def text_to_speech(self, 
                      text: str,
                      voice: str = "longxiaochun",
                      format: str = "mp3",
                      sample_rate: int = 16000) -> Optional[str]:
        """
        文本转语音
        
        Args:
            text: 要合成的文本
            voice: 音色（longxiaochun, longxiaoxia 等）
            format: 音频格式（mp3, wav）
            sample_rate: 采样率
            
        Returns:
            音频文件路径或 URL
        """
        if not self._init_client():
            print("CosyVoice 客户端未初始化")
            return None
        
        try:
            from alibabacloud_cosyvoice20220616 import models as cosyvoice_models
            import uuid
            
            # 构造请求
            request = cosyvoice_models.SynthesizeSpeechRequest(
                text=text,
                voice=voice,
                format=format,
                sample_rate=sample_rate
            )
            
            # 调用 API
            response = self._client.synthesize_speech(request)
            
            # 保存音频文件
            filename = f"{uuid.uuid4().hex}.{format}"
            output_path = os.path.join(self.output_dir, filename)
            
            with open(output_path, 'wb') as f:
                f.write(response.body.audio_data)
            
            print(f"语音合成成功: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"语音合成失败: {e}")
            return None
    
    def batch_text_to_speech(self, texts: list) -> list:
        """
        批量文本转语音
        
        Args:
            texts: 文本列表
            
        Returns:
            音频文件路径列表
        """
        results = []
        for text in texts:
            audio_path = self.text_to_speech(text)
            if audio_path:
                results.append(audio_path)
        
        return results
    
    def get_available_voices(self) -> list:
        """
        获取可用的音色列表
        
        Returns:
            音色列表
        """
        # 常用音色列表
        voices = [
            "longxiaochun",  # 龙小春（女声）
            "longxiaoxia",   # 龙小夏（女声）
            "longxiaoqiu",   # 龙小秋（女声）
            "longxiaodong",  # 龙小冬（男声）
        ]
        return voices


if __name__ == "__main__":
    # 测试代码
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    appkey = os.getenv("COSYVOICE_APPKEY")
    token = os.getenv("COSYVOICE_TOKEN")
    
    if appkey and token:
        client = CosyVoiceClient(appkey, token)
        
        # 测试语音合成
        text = "您好，这是心血管疾病预测系统的语音测试。"
        audio_path = client.text_to_speech(text)
        
        if audio_path:
            print(f"音频已保存到: {audio_path}")
    else:
        print("请设置 COSYVOICE_APPKEY 和 COSYVOICE_TOKEN 环境变量")

