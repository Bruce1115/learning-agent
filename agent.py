import requests
import json

def call_qwen_with_requests(user_input, system_prompt="你是一个专业的AI助手"):
    # 1. 设置 API 地址和请求头 (Headers) [1]
    # 这里手动设置 API Key，模拟底层协议细节
    url = "https://ws-tgy7y4p9nn18imng.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-ws-H.EDPEHEX.jQ1o.MEUCIQDq1YvWoKKhih0s1bgGbvCvxpQ1iVptn7XHjnqRsIeelgIgA8U3lnvZZHJO8kPumluNjvUVhOorBmsAlHh0MczjIwU"
    }

    # 2. 构建符合 API 规范的 JSON 数据包 [1]
    # 包含模型 ID、Prompt (角色设定) 和参数
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    # 3. 发送请求
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 4. 解析返回的 JSON 响应 [1]
        if response.status_code == 200:
            result = response.json()
            # 提取模型生成的文本内容
            # 这是结构化输出的本质：从嵌套的字典中获取 'content'
            content = result['choices']['message']['content']
            return content
        else:
            return f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
            
    except Exception as e:
        return f"发生异常: {str(e)}"

# --- 测试调用 ---
user_query = "请简要介绍阿里云百炼平台"
print("--- 正在通过 requests 访问 LLM ---")
answer = call_qwen_with_requests(user_query)
print(f"LLM 响应内容:\n{answer}")