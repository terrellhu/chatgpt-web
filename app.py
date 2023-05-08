import os
import hashlib
from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_cors import CORS

from ai.chat import chat_with_openai
from ai.embedding import embedding_file, talk_file, talk_file_stuff
from common.config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db

config = Config()

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)
app.secret_key = config.APP_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/db/data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
from models.user import User
from models.chat_content import ChatContent
from models.user_chat import UserChat

migrate = Migrate(app, db)

from routes.chat_routes import chat
from routes.auth_routes import auth
from routes.chat_stream_routes import chatsse

from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)


app.register_blueprint(auth)
app.register_blueprint(chat)
app.register_blueprint(chatsse)

chat_histories = {}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
    app.run(host='0.0.0.0', port=5000, debug=True)
