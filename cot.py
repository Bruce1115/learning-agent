import requests
import json
import os

# Toggle debug printing
DEBUG = False

def call_qwen_with_requests(user_input, system_prompt):
    # 1. 设置 API 地址和请求头 (Headers) [1]
    # 这里手动设置 API Key，模拟底层协议细节
    url = "https://ws-tgy7y4p9nn18imng.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"
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
        if DEBUG:
            print("DEBUG: about to call requests.post")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if DEBUG:
            print("DEBUG: response.status_code ->", response.status_code)
            try:
                parsed = response.json()
                print("DEBUG: response.json ->\n", json.dumps(parsed, ensure_ascii=False, indent=2))
            except ValueError:
                print("DEBUG: response.text (non-json) ->", repr(response.text))
        
        # 4. 解析返回的 JSON 响应 [1]
        if response.status_code == 200:
            result = response.json()
            try:
                choices = result.get('choices', [])
                outputs = []
                if isinstance(choices, list) and len(choices) > 0:
                    for idx, ch in enumerate(choices, start=1):
                        if not isinstance(ch, dict):
                            continue
                        message = ch.get('message', {})
                        content = None
                        if isinstance(message, dict):
                            content = message.get('content')
                        # 支持 content 既是字符串也可能是嵌套结构的情况
                        if isinstance(content, str):
                            outputs.append(content)
                            continue
                        if isinstance(content, dict) and 'content' in content:
                            inner = content['content']
                            outputs.append(inner if isinstance(inner, str) else str(inner))
                            continue
                        # 有些模型使用 top-level text 字段或直接把 message.content 放在不同位置
                        if isinstance(ch.get('text'), str):
                            outputs.append(ch.get('text'))
                            continue

                # 如果通过 choices 没有收集到任何输出，尝试其他回退字段（返回原始文本，不在这里格式化）
                if not outputs:
                    if isinstance(result.get('text'), str):
                        outputs.append(result.get('text'))
                    elif isinstance(result.get('message'), dict) and isinstance(result['message'].get('content'), str):
                        outputs.append(result['message']['content'])

                if outputs:
                    return outputs

                return [f"无法从响应中提取内容: {json.dumps(result, ensure_ascii=False)[:1000]}"]
            except Exception as e:
                return f"解析响应时发生异常: {str(e)}"
        else:
            return f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"发生异常: {str(e)}"

# --- 测试调用 ---
system_prompt="你是一个专业的AI助手,你要按照COT的逻辑，Step by step”地思考"
user_query = "如果 A 比 B 快，C 比 A 慢但比 B 快，请排列顺序并说明拆解逻辑。"
print("--- 正在通过 requests 访问 LLM ---")
answer = call_qwen_with_requests(user_query,system_prompt)

print("LLM 响应内容:")
# 统一在这里处理：保证为列表、把字面 "\\n" 替换为真实换行，并添加编号前缀
if not isinstance(answer, list):
    answer = [str(answer)]
if DEBUG:
    print("DEBUG: raw answer items:")
    for i, a in enumerate(answer, start=1):
        print(i, repr(a)[:200])
    try:
        print("DEBUG: raw answer json ->\n", json.dumps(answer, ensure_ascii=False, indent=2)[:2000])
    except Exception:
        pass
cleaned = []
for idx, item in enumerate(answer, start=1):
    s = item if isinstance(item, str) else str(item)
    s = s.replace('\\n', '\n')
    if len(answer) > 1:
        cleaned.append(f"第{idx}个回答\n{s}")
    else:
        cleaned.append(s)
print("\n\n".join(cleaned))

"""
(.venv) brucelee@Bruce-Mac learning-agent % python3 cot.py
--- 正在通过 requests 访问 LLM ---
LLM 响应内容:
我们来**逐步拆解（Chain-of-Thought, COT）**这个逻辑排序问题：

---

### 🌟 题干信息：
1. **A 比 B 快**
   → 速度关系：A > B
   （“快”即速度大，按速度从高到低排序）

2. **C 比 A 慢，但比 B 快**
   → 即：A > C 且 C > B
   → 合起来：A > C > B

---

### ✅ 步骤拆解：

- Step 1：由“A 比 B 快”得：**A > B**
- Step 2：由“C 比 A 慢”得：**A > C**
- Step 3：由“C 比 B 快”得：**C > B**
- Step 4：整合三个不等式：
  - A > C（Step 2）
  - C > B（Step 3）
  ⇒ 传递得：**A > C > B**
  （同时这也满足 Step 1 的 A > B，一致无矛盾）

---

### ✅ 最终速度从**快到慢**的顺序是：
**A ＞ C ＞ B**

（即：A 最快，C 居中，B 最慢）

---

### 🔍 补充说明（避免常见误解）：
- “快/慢”比较的是**速度大小**，不是时间或距离；默认在同一任务/距离下比较（如跑100米用时越少越快 → 速度越大）。
- 所有比较均为严格不等（“比…快/慢”通常意味着严格大于/小于，不包含相等）。
- 无其他隐含条件（如加速度、平均/瞬时速度等），按常规语义理解为**稳态或整体速度比较**。

---

✅ 答案：**A > C > B**（从快到慢）
逻辑链：A > B，A > C > B ⇒ 三者唯一确定序。

"""