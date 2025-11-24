"""
语音问答模块
集成 DeepSeek 文本生成和 CosyVoice 语音合成
"""

import os
import sys
from typing import Dict, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger
from utils.audio_utils import save_audio_file, ensure_audio_directory
from utils.config import Config

# 设置日志
logger = setup_logger('audio', log_dir='./logs')


class QAudioSystem:
    """语音问答系统"""
    
    def __init__(self):
        """初始化系统"""
        self.config = Config()
        self.llm = None
        self.tts_client = None
        
        logger.info("初始化语音问答系统")
        
        # 确保音频目录存在
        ensure_audio_directory()
    
    def _init_deepseek(self):
        """初始化 DeepSeek LLM"""
        if self.llm is not None:
            return True
        
        try:
            from langchain_openai import ChatOpenAI
            
            # 检查 API Key
            if not self.config.DEEPSEEK_API_KEY:
                logger.error("DEEPSEEK_API_KEY 未配置")
                return False
            
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=self.config.DEEPSEEK_API_KEY,
                base_url=self.config.DEEPSEEK_API_URL,
                temperature=0.7,
                max_tokens=200
            )
            
            logger.info("DeepSeek LLM 初始化成功")
            return True
            
        except ImportError:
            logger.error("请安装 langchain-openai: pip install langchain-openai")
            return False
        except Exception as e:
            logger.error(f"DeepSeek 初始化失败: {e}")
            return False
    
    def _init_cosyvoice(self):
        """初始化 CosyVoice TTS"""
        if self.tts_client is not None:
            return True
        
        try:
            # 使用阿里云 DashScope SDK
            # 参考: https://help.aliyun.com/zh/model-studio/cosyvoice-python-sdk
            import dashscope
            from dashscope.audio.tts_v2 import SpeechSynthesizer
            
            # 检查 API Key
            if not self.config.COSYVOICE_APPKEY:
                logger.warning("COSYVOICE_APPKEY 未配置，语音合成功能不可用")
                return False
            
            # 设置 API Key
            dashscope.api_key = self.config.COSYVOICE_APPKEY
            
            # 保存 SpeechSynthesizer 类
            self.tts_client = SpeechSynthesizer
            
            logger.info("CosyVoice TTS 初始化成功")
            return True
            
        except ImportError as e:
            logger.error(f"请安装 dashscope: pip install dashscope (错误: {e})")
            return False
        except Exception as e:
            logger.error(f"CosyVoice 初始化失败: {e}")
            return False
    
    def generate_answer(self, question: str) -> Optional[str]:
        """
        使用 DeepSeek 生成文本回答
        
        Args:
            question: 用户问题
            
        Returns:
            str: AI 回答文本
        """
        logger.info(f"生成回答，问题: {question[:50]}...")
        
        # 初始化 LLM
        if not self._init_deepseek():
            return None
        
        try:
            # 构建系统提示
            system_prompt = "你是一个专业的心血管健康顾问，能够回答关于心血管疾病预防、治疗和健康生活方式的问题。请用简洁、专业的语言回答。"
            
            # 调用 LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            logger.info(f"回答生成成功，长度: {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            return None
    
    def synthesize_audio(self, text: str, max_retries: int = None) -> Optional[str]:
        """
        使用 CosyVoice 合成语音（带重试机制）
        
        Args:
            text: 要合成的文本
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            str: 音频 URL 路径
        """
        logger.info(f"合成语音，文本长度: {len(text)}")
        
        # 初始化 TTS
        if not self._init_cosyvoice():
            return None
        
        # 使用配置中的重试次数
        if max_retries is None:
            max_retries = self.config.COSYVOICE_MAX_RETRIES
        
        # 获取超时时间（毫秒）
        timeout_ms = self.config.COSYVOICE_TIMEOUT * 1000
        
        logger.info(f"超时设置: {self.config.COSYVOICE_TIMEOUT}秒, 最大重试: {max_retries}次")
        
        # 重试机制
        for attempt in range(max_retries):
            try:
                logger.info(f"语音合成尝试 {attempt + 1}/{max_retries}")
                
                # 根据官方文档，使用 SpeechSynthesizer 进行同步调用
                # 参考: https://help.aliyun.com/zh/model-studio/cosyvoice-python-sdk
                # 示例代码：
                # synthesizer = SpeechSynthesizer(model="cosyvoice-v2", voice="longxiaochun_v2")
                # audio = synthesizer.call("今天天气怎么样？")
                
                # 每次调用前需要重新初始化 SpeechSynthesizer 实例
                synthesizer = self.tts_client(
                    model='cosyvoice-v1',      # 使用 v1 模型
                    voice='longxiaochun'       # v1 对应的音色
                )
                
                # 同步调用，阻塞式返回完整音频数据
                # timeout_millis: 超时时间（毫秒），从配置读取
                audio_data = synthesizer.call(text, timeout_millis=timeout_ms)
                
                # 保存音频文件
                if audio_data:
                    file_path, audio_url = save_audio_file(audio_data)
                    logger.info(f"音频合成成功: {audio_url}")
                    logger.info(f"Request ID: {synthesizer.get_last_request_id()}")
                    logger.info(f"首包延迟: {synthesizer.get_first_package_delay()}ms")
                    return audio_url
                else:
                    logger.error("音频合成失败：无数据返回")
                    if attempt < max_retries - 1:
                        logger.info(f"准备重试...")
                        import time
                        time.sleep(2)  # 等待 2 秒后重试
                        continue
                    return None
                    
            except TimeoutError as e:
                logger.warning(f"第 {attempt + 1} 次尝试超时: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"准备重试...")
                    import time
                    time.sleep(2)  # 等待 2 秒后重试
                    continue
                else:
                    logger.error(f"语音合成失败：已达到最大重试次数 {max_retries}")
                    return None
                    
            except Exception as e:
                logger.error(f"音频合成失败: {e}")
                logger.exception("详细错误信息:")
                if attempt < max_retries - 1:
                    logger.info(f"准备重试...")
                    import time
                    time.sleep(2)  # 等待 2 秒后重试
                    continue
                return None
        
        return None
    
    def qa_pipeline(self, question: str) -> Dict:
        """
        完整的问答流程
        
        Args:
            question: 用户问题
            
        Returns:
            dict: 包含文本回答和音频 URL
        """
        logger.info("=" * 50)
        logger.info("开始语音问答流程")
        logger.info(f"问题: {question}")
        
        result = {
            'success': False,
            'text': '',
            'audio_url': None,
            'error': None
        }
        
        try:
            # 1. 生成文本回答
            answer = self.generate_answer(question)
            
            if not answer:
                result['error'] = '文本生成失败'
                logger.error(result['error'])
                return result
            
            result['text'] = answer
            
            # 2. 合成语音
            audio_url = self.synthesize_audio(answer)
            
            if audio_url:
                result['audio_url'] = audio_url
                result['success'] = True
                logger.info("语音问答流程完成")
            else:
                # 即使语音合成失败，也返回文本
                result['success'] = True
                result['error'] = '语音合成失败，仅返回文本'
                logger.warning(result['error'])
            
        except Exception as e:
            result['error'] = f'处理失败: {str(e)}'
            logger.error(result['error'], exc_info=True)
        
        logger.info("=" * 50)
        return result


# 全局实例
_qa_system = None


def get_qa_system() -> QAudioSystem:
    """获取语音问答系统实例（单例模式）"""
    global _qa_system
    if _qa_system is None:
        _qa_system = QAudioSystem()
    return _qa_system


def generate_answer(question: str) -> Optional[str]:
    """
    生成文本回答（便捷函数）
    
    Args:
        question: 用户问题
        
    Returns:
        str: AI 回答
    """
    system = get_qa_system()
    return system.generate_answer(question)


def synthesize_audio(text: str) -> Optional[str]:
    """
    合成语音（便捷函数）
    
    Args:
        text: 要合成的文本
        
    Returns:
        str: 音频 URL
    """
    system = get_qa_system()
    return system.synthesize_audio(text)


def qa_pipeline(question: str) -> Dict:
    """
    完整问答流程（便捷函数）
    
    Args:
        question: 用户问题
        
    Returns:
        dict: 结果字典
    """
    system = get_qa_system()
    return system.qa_pipeline(question)


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("测试语音问答系统")
    print("=" * 60)
    
    # 测试问题
    test_question = "如何预防心血管疾病？"
    
    print(f"\n问题: {test_question}\n")
    
    # 执行问答流程
    result = qa_pipeline(test_question)
    
    if result['success']:
        print("✅ 成功!")
        print(f"\n回答: {result['text']}")
        if result['audio_url']:
            print(f"\n音频: {result['audio_url']}")
        else:
            print(f"\n⚠️ {result.get('error', '音频生成失败')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    
    print("\n" + "=" * 60)

