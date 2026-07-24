import os
import re
import requests
import json



# =========================
# 1. LLM API调用
# =========================

API_URL = "https://ws-tgy7y4p9nn18imng.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

print("API Key:", API_KEY)


def call_llm(messages):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "qwen-plus",
        "messages": messages,
        "temperature": 0
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]



# =========================
# 2. 定义工具
# =========================


def weather_forecast(city, date):

    return {
        "city": city,
        "date": date,
        "weather": "多云",
        "temperature": "23-28℃"
    }



TOOLS = {

    "weather_forecast": weather_forecast

}



# =========================
# 3. ReAct Prompt
# =========================


SYSTEM_PROMPT = """

你是一个ReAct Agent。

你必须严格按照下面格式工作：


Thought:
你的思考过程


Action:
工具名称


Action Input:
JSON参数


收到Observation后继续。


如果信息足够：

Answer:
最终答案


可用工具：

weather_forecast:
查询天气

参数:

{
 "city": "城市",
 "date": "日期"
}


"""


# =========================
# 4. 解析Action
# =========================


def parse_action(text):

    action_match = re.search(
        r"Action:\s*(\w+)",
        text
    )


    input_match = re.search(
        r"Action Input:\s*(\{.*?\})",
        text,
        re.S
    )


    if action_match and input_match:

        action_name = action_match.group(1)

        args = json.loads(
            input_match.group(1)
        )

        return action_name,args


    return None,None



# =========================
# 5. ReAct Agent Loop
# =========================


def react_agent(user_question):


    messages=[

        {
            "role":"system",
            "content":SYSTEM_PROMPT
        },

        {
            "role":"user",
            "content":user_question
        }

    ]


    while True:


        print("\n====== Calling LLM ======")


        response = call_llm(messages)


        print(response)



        # -----------------
        # 判断是否Action
        # -----------------

        action,args = parse_action(response)


        if action:
            print("\n执行工具:")
            print(action,args)
            tool = TOOLS[action]
            observation = tool(**args)
            print(
                "\nObservation:",
                observation
            )
            # 加入上下文
            messages.append(
                {
                    "role":"assistant",
                    "content":response
                }
            )
            messages.append(
                {
                    "role":"user",
                    "content":
                    f"""
Observation:

{json.dumps(
    observation,
    ensure_ascii=False
)}

请继续推理。
"""
                }
            )



        else:

            # 没有Action
            # 说明模型已经回答

            return response




# =========================
# 6. 测试
# =========================


answer = react_agent(
    "惠州大亚湾明天天气如何？"
)


print("\n========== FINAL ==========")

print(answer)



