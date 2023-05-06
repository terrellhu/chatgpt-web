import os
import hashlib
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from ai.chat import chat_with_openai
from ai.embedding import embedding_file, talk_file, talk_file_stuff
from common.config import Config

config = Config()


app = Flask(__name__)
CORS(app)

chat_histories = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # 从 JSON 数据中提取值
    userid = data.get("userid")
    message = data.get("message")

    # 如果用户 ID 不存在于 chat_histories，则初始化一个空列表
    if userid not in chat_histories:
        chat_histories[userid] = []

    reply = chat_with_openai(userid, message, chat_histories[userid])

    return jsonify({'reply': reply})


@app.route('/chat_file', methods=['POST'])
def chat_file():
    data = request.get_json()
    # 从 JSON 数据中提取值
    userid = data.get("userid")
    message = data.get("message")

    # 如果用户 ID 不存在于 chat_histories，则初始化一个空列表
    if userid not in chat_histories:
        chat_histories[userid] = []

    reply = talk_file_stuff(userid, message, chat_histories[userid])

    return jsonify({'reply': reply})


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    userid = request.form.get("userid")

    if uploaded_file:
        allowed_extensions = [".txt", ".pdf"]

        # 获取上传文件的扩展名
        _, file_extension = os.path.splitext(uploaded_file.filename)
        file_extension = file_extension.lower()
        # 检查文件扩展名是否在允许的扩展名列表中
        if file_extension not in allowed_extensions:
            return jsonify({"error": f"Invalid file type. Allowed file types: {', '.join(allowed_extensions)}"})

        # 计算文件的 MD5 值
        md5 = hashlib.md5()
        for chunk in iter(lambda: uploaded_file.read(4096), b""):
            md5.update(chunk)
        uploaded_file.seek(0)  # 将文件指针重置到文件开头，以便后续操作

        md5_hash = md5.hexdigest()
        saved_file_name = f"{config.DATA_UPLOAD_PATH}{md5_hash}-{uploaded_file.filename}-{file_extension}"

        # 获取文件所在的目录
        folder_path = os.path.dirname(saved_file_name)

        # 如果目录不存在，则创建目录
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
        # 检查文件是否已存在，避免重复写入
        if not os.path.exists(saved_file_name):
            uploaded_file.save(saved_file_name)
        else:
            return f"文件已存在，不再重复写入: {saved_file_name}"
        # chat_history[userid+saved_file_name] = saved_file_name

        embedding_file(userid, saved_file_name)

        pass

    return jsonify({"message": "文件上传成功"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
