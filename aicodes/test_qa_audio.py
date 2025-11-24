"""
测试语音问答系统
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio.qa_audio import qa_pipeline


def test_qa_audio():
    """测试语音问答功能"""
    print("=" * 60)
    print("测试 AI 语音问答系统")
    print("=" * 60)
    
    # 测试问题列表
    test_questions = [
        "如何预防心血管疾病？",
        "高血压患者应该注意什么？",
        "心血管疾病的早期症状有哪些？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}/{len(test_questions)}")
        print(f"问题: {question}")
        print("=" * 60)
        
        # 执行问答
        result = qa_pipeline(question)
        
        if result['success']:
            print("\n✅ 成功!")
            print(f"\n回答:\n{result['text']}")
            
            if result['audio_url']:
                print(f"\n🔊 音频: {result['audio_url']}")
            else:
                print(f"\n⚠️ 警告: {result.get('error', '音频生成失败')}")
        else:
            print(f"\n❌ 失败: {result.get('error')}")
        
        print("\n" + "=" * 60)
        
        # 询问是否继续
        if i < len(test_questions):
            choice = input("\n继续下一个测试？(y/n): ").strip().lower()
            if choice != 'y':
                break
    
    print("\n测试完成!")


if __name__ == '__main__':
    try:
        test_qa_audio()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()

