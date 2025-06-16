from .base import db, BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import foreign

class Message(BaseModel):
    __tablename__ = 'message'

    chat_uuid = db.Column(db.String(36), ForeignKey('chat.uuid'), nullable=False, index=True)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)

    chat = relationship(
        'Chat',
        back_populates='messages',
        primaryjoin="Chat.uuid == foreign(Message.chat_uuid)",
        foreign_keys='Message.chat_uuid'
    )

    def __repr__(self):
        return f"<Chat Message from {self.sender}>"
