from models import db
from datetime import datetime


class UserChat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    chat_name = db.Column(db.String(128), nullable=True)
    model = db.Column(db.String(64), nullable=True)
    last_chat_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserChat username={self.username}, chat_id={self.chat_id}, chat_name={self.chat_name}, model={self.model}, lasttime={self.last_chat_time}> '
