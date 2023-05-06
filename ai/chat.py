import openai

from common.config import Config

config = Config()


def chat_with_openai(user_id, message, history):
    openai.api_key = config.OPENAI_API_KEY
    # 将用户的当前消息添加到历史记录
    history.insert(0, {"role": "system", "content": f"{message}", "source": f"{user_id}"})

    # 生成 OpenAI 输入消息列表
    # openai_messages = [{"role": msg["role"], "content": msg["content"]} for msg in reversed(history)]
    max_iterations = 5  # 设置最大迭代次数

    openai_messages = []
    for index, msg in enumerate(reversed(history)):
        if index >= max_iterations:
            break
        openai_messages.append({"role": msg["role"], "content": msg["content"]})

    # 调用 ChatOpenAI API
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=openai_messages,
        max_tokens=4096,
        temperature=0.5,
    )

    # 从响应中提取回复
    reply = response.choices[0].message["content"].strip()

    # 将回复添加到历史记录
    history.insert(0, {"role": "assistant", "content": reply, "source": "bot"})

    # 更新用户的聊天记录
    # chat_histories[user_id] = history

    return reply
