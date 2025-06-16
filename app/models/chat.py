from .base import db, BaseModel
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.orm import foreign

class Chat(BaseModel):
    __tablename__ = 'chat'

    # Use a UUID for the chat session ID
    uuid = db.Column(db.String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    messages = relationship(
        'Message',
        back_populates='chat',
        primaryjoin="Chat.uuid == foreign(Message.chat_uuid)",
        foreign_keys='Message.chat_uuid',
        order_by="Message.created",
        cascade='all, delete-orphan',
        lazy='dynamic'  # Consider using 'dynamic' for large datasets
    )

    def __repr__(self):
        return f"<UUID for Chat: {self.uuid}>"
