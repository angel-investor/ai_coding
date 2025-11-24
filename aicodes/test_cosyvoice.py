"""
测试 CosyVoice 语音合成功能
"""

import os
import sys
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import Config
from audio.qa_audio import QAudioSystem


def test_import():
    """测试导入"""
    print("=" * 50)
    print("测试 1: 导入 dashscope")
    print("=" * 50)
    
    try:
        import dashscope
        print("[OK] dashscope 导入成功")
        
        from dashscope import SpeechSynthesizer
        print("[OK] SpeechSynthesizer 导入成功")
        print(f"  类型: {SpeechSynthesizer}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 导入失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n" + "=" * 50)
    print("测试 2: 检查配置")
    print("=" * 50)
    
    config = Config()
    
    print(f"DeepSeek API Key: {'已配置' if config.DEEPSEEK_API_KEY else '未配置'}")
    print(f"DeepSeek API URL: {config.DEEPSEEK_API_URL}")
    print(f"CosyVoice AppKey: {'已配置' if config.COSYVOICE_APPKEY else '未配置'}")
    
    if not config.DEEPSEEK_API_KEY:
        print("\n⚠️  警告: DeepSeek API Key 未配置")
        print("   运行: 配置API_KEY.bat")
        return False
    
    if not config.COSYVOICE_APPKEY:
        print("\n⚠️  警告: CosyVoice AppKey 未配置")
        print("   语音合成功能将不可用")
        print("   但文本问答功能可以正常使用")
    
    return True


def test_initialization():
    """测试初始化"""
    print("\n" + "=" * 50)
    print("测试 3: 初始化 QAudioSystem")
    print("=" * 50)
    
    try:
        qa_system = QAudioSystem()
        print("✓ QAudioSystem 初始化成功")
        return qa_system
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_text_generation(qa_system):
    """测试文本生成"""
    print("\n" + "=" * 50)
    print("测试 4: 文本生成")
    print("=" * 50)
    
    question = "什么是心血管疾病？"
    print(f"问题: {question}")
    
    try:
        answer = qa_system.generate_answer(question)
        if answer:
            print(f"✓ 文本生成成功")
            print(f"  回答长度: {len(answer)} 字符")
            print(f"  回答内容: {answer[:100]}...")
            return answer
        else:
            print("✗ 文本生成失败")
            return None
    except Exception as e:
        print(f"✗ 文本生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_audio_synthesis(qa_system, text):
    """测试语音合成"""
    print("\n" + "=" * 50)
    print("测试 5: 语音合成")
    print("=" * 50)
    
    if not text:
        print("⊘ 跳过测试（无文本）")
        return False
    
    print(f"文本长度: {len(text)} 字符")
    
    try:
        audio_url = qa_system.synthesize_audio(text[:50])  # 只合成前50字符
        if audio_url:
            print(f"✓ 语音合成成功")
            print(f"  音频 URL: {audio_url}")
            return True
        else:
            print("✗ 语音合成失败（可能未配置 CosyVoice API Key）")
            return False
    except Exception as e:
        print(f"✗ 语音合成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n")
    print("=" * 50)
    print("  CosyVoice 语音合成功能测试")
    print("=" * 50)
    
    # 测试 1: 导入
    if not test_import():
        print("\n❌ 测试失败: 无法导入 dashscope")
        print("   解决方案: pip install dashscope")
        return
    
    # 测试 2: 配置
    if not test_config():
        print("\n❌ 测试失败: 配置不完整")
        return
    
    # 测试 3: 初始化
    qa_system = test_initialization()
    if not qa_system:
        print("\n❌ 测试失败: 无法初始化系统")
        return
    
    # 测试 4: 文本生成
    answer = test_text_generation(qa_system)
    
    # 测试 5: 语音合成
    test_audio_synthesis(qa_system, answer)
    
    # 总结
    print("\n" + "=" * 50)
    print("  测试完成")
    print("=" * 50)
    print("\n如果所有测试通过，系统已准备就绪！")
    print("访问: http://localhost:5000/web/qa_audio.html")
    print("\n")


if __name__ == "__main__":
    main()

