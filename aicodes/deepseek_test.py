import os
from dotenv import load_dotenv
import requests

def test_deepseek_api():
    # 加载 .env
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY1")
    base_url = os.getenv("base_url1").replace('"', '').replace("'", "")

    if not api_key or not base_url:
        print("❌ 未成功读取 API Key 或 Base URL，请检查 .env 文件格式。")
        return

    url = f"{base_url}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "你可以正常响应吗？"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        print("状态码:", response.status_code)
        print("返回内容：")
        print(response.json())

    except Exception as e:
        print("❌ 请求失败：", e)


if __name__ == "__main__":
    test_deepseek_api()
