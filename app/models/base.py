from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True  # Ensures that no table is created for this base class

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=func.current_timestamp())
    updated = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def save(self):
        """Save the object to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the object from the database."""
        db.session.delete(self)
        db.session.commit()
