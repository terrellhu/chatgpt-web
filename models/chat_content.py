from models import db
from datetime import datetime


class ChatContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    from_user = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, chat_id, content, from_user):
        self.chat_id = chat_id
        self.content = content
        self.from_user = from_user

    def __repr__(self):
        return f'<ChatContent {self.id}>'
