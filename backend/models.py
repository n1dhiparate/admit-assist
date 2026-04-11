from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ---------------- STUDENT MODEL ----------------
class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # ✅ SAFE DEFAULT (IMPORTANT FIX)
    onboarding_status = db.Column(
        db.JSON,
        nullable=False,
        default=lambda: {
            "documents": False,
            "fees": False,
            "registration": False
        }
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "onboarding_status": self.onboarding_status
        }


# ---------------- CONVERSATION MEMORY ----------------
class ConversationMessage(db.Model):
    __tablename__ = 'conversation_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    student_id = db.Column(
        db.String(50),
        db.ForeignKey('students.student_id'),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )  # user / assistant / tool / system

    content = db.Column(db.Text, nullable=True)

    tool_call_id = db.Column(db.String(100), nullable=True)

    tool_calls = db.Column(db.JSON, nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    student = db.relationship(
        'Student',
        backref=db.backref('messages', lazy=True)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "role": self.role,
            "content": self.content,
            "tool_call_id": self.tool_call_id,
            "tool_calls": self.tool_calls,
            "timestamp": self.timestamp.isoformat()
        }