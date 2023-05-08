import json

from flask import Flask, render_template, Blueprint, request, jsonify, Response
from flask_login import login_required
from app import db
import openai
from models.chat_content import ChatContent
from common.config import Config

config = Config()

openai.api_key = config.OPENAI_API_KEY
openai.api_base = config.OPENAI_API_BASE

chatsse = Blueprint('chatsse', __name__)


def generate_chat_stream(chatid, openai_params):
    response_text_list = []

    # 使用流式处理接口调用 OpenAI API
    for chat_response in openai.Completion.stream(**openai_params):
        response_text = chat_response.choices[0].text
        response_text_list.append(response_text)
        # 将获得的回答逐个发送给客户端
        yield f"data: {response_text}\n\n"

    # 将整个回答存入数据库
    full_response_text = "".join(response_text_list)
    chat_content = ChatContent(chat_id=chatid, content=full_response_text, from_user="assistant")
    db.session.add(chat_content)
    db.session.commit()


@login_required
@chatsse.route('/chat_stream', methods=['POST'])
def chat_stream():
    message = request.form.get('message')
    username = request.form.get('username')
    chatid = request.form.get('chatid')
    if username is None or username == "" or message is None or message == "" or chatid is None or chatid == "":
        return jsonify({'success': False, 'message': 'Invalid username or message or chatid'})

    model = request.form.get('model')
    if model is None:
        model = "gpt-3.5-turbo"

    # 查询历史 n 条记录作为会话上下文
    recent_chat_records = ChatContent.query.filter_by(chat_id=chatid).order_by(
        ChatContent.created_at.desc()).limit(5).all()
    recent_chat_messages = [
        {"role": record.from_user, "content": record.content} for record in
        recent_chat_records]

    # 配置 OpenAI 对话接口参数
    openai_params = {
        "engine": model,
        "messages": [{"role": "system", "content": "You are now chatting with an AI."}] + recent_chat_messages + [
            {"role": "user", "content": message}],
        "user": username,
        "stream": True
    }

    # 插入问题到db
    chat_content = ChatContent(chat_id=chatid, content=message, from_user="user")
    db.session.add(chat_content)
    db.session.commit()

    return Response(generate_chat_stream(openai_params), content_type='text/event-stream')
