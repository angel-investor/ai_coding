"""
DeepSeek API客户端
用于调用DeepSeek API生成文本回答
"""

import requests
from typing import Optional, Dict, List
import json


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.deepseek.com/v1"):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: API密钥
            api_url: API地址
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict:
        """
        调用聊天完成接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            Dict: API响应
        """
        endpoint = f"{self.api_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API调用失败: {e}")
            return {"error": str(e)}
    
    def ask_question(
        self,
        question: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        提问并获取回答
        
        Args:
            question: 用户问题
            system_prompt: 系统提示词
            context: 上下文信息
            
        Returns:
            str: AI回答
        """
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            messages.append({
                "role": "system",
                "content": "你是一个专业的心血管疾病健康顾问，能够回答关于心血管健康的问题。"
            })
        
        # 添加上下文
        if context:
            messages.append({
                "role": "user",
                "content": f"背景信息：{context}"
            })
        
        # 添加用户问题
        messages.append({
            "role": "user",
            "content": question
        })
        
        # 调用API
        response = self.chat_completion(messages)
        
        # 提取回答
        if "error" in response:
            return f"抱歉，生成回答时出错：{response['error']}"
        
        try:
            answer = response['choices'][0]['message']['content']
            return answer
        except (KeyError, IndexError) as e:
            return f"解析响应失败：{e}"
    
    def generate_health_advice(
        self,
        user_data: Dict,
        prediction_result: Dict
    ) -> str:
        """
        根据用户数据和预测结果生成健康建议
        
        Args:
            user_data: 用户健康数据
            prediction_result: 模型预测结果
            
        Returns:
            str: 健康建议
        """
        risk_level = prediction_result.get('risk_level', '未知')
        probability = prediction_result.get('probability', {}).get('positive', 0)
        
        context = f"""
        用户健康数据：
        {json.dumps(user_data, ensure_ascii=False, indent=2)}
        
        预测结果：
        - 风险等级：{risk_level}
        - 患病概率：{probability:.2%}
        """
        
        question = "请根据以上数据，给出详细的健康建议和生活方式改善建议。"
        
        return self.ask_question(question, context=context)
