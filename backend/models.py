from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Store onboarding checklist as JSON object
    onboarding_status = db.Column(db.JSON, nullable=False, default={
        "doc": False, 
        "fee": False, 
        "reg": False, 
        "hostel": False, 
        "lms": False
    })

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "onboarding_status": self.onboarding_status
        }
