from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os
import requests
from datetime import timedelta
from backend.rag.rag import retrieve_context

try:
    from groq import Groq
except ImportError:
    Groq = None

# Import new ORM and Auth tools
from backend.models import db, Student 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Load API key and Database URL
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------------------
# ORM & Auth Configuration
# ----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    # Will create tables defined in models.py if they don't exist
    db.create_all()

    # Automatically create our default test user if missing
    if not Student.query.filter_by(student_id='IT-2026-NP').first():
        test_student = Student(
            student_id='IT-2026-NP',
            name='Nidhi Parate',
            password_hash=generate_password_hash('password123'),
        )
        db.session.add(test_student)
        db.session.commit()

# ----------------------------
# AUTHENTICATION ROUTES
# ----------------------------
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    student_id = data.get('student_id')
    name = data.get('name')
    password = data.get('password')

    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({"error": "Student ID already exists"}), 400

    new_student = Student(
        student_id=student_id,
        name=name,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"success": True, "message": "User registered successfully"})


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    student = Student.query.filter_by(student_id=student_id).first()
    if student and check_password_hash(student.password_hash, password):
        access_token = create_access_token(identity=student_id)
        return jsonify({"access_token": access_token, "student_id": student.student_id, "name": student.name})
    
    return jsonify({"error": "Invalid credentials"}), 401


# ----------------------------
# Original Routes (Updated to ORM)
# ----------------------------
@app.route('/admin/seed', methods=['POST'])
def seed_database():
    try:
        Student.query.delete()
        db.session.commit()

        first_names = ["Arjun", "Sana", "Rohan", "Ananya", "Vikram", "Isha", "Rahul", "Priya"]
        last_names = ["Sharma", "Verma", "Patel", "Mehta", "Nair", "Gupta", "Rao", "Joshi"]

        for i in range(1, 51):
            s_id = f"IT-2026-{1000 + i}"
            s_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            status = {
                "documents": random.choice([True, False]),
                "fees": random.choice([True, False]),
                "registration": random.choice([True, False])
            }

            new_student = Student(
                student_id=s_id,
                name=s_name,
                password_hash=generate_password_hash("password123"),
                onboarding_status=status
            )
            db.session.add(new_student)

        # Restore main user
        test_student = Student(student_id='IT-2026-NP', name='Nidhi Parate', password_hash=generate_password_hash('password123'))
        db.session.add(test_student)

        db.session.commit()

        return jsonify({"status": "success"})

    except Exception as e:
        print("SEED ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/get-onboarding', methods=['GET'])
@jwt_required(optional=True)
def get_onboarding():
    # If no token is provided, fall back to default user to preserve old UI flow
    current_user_id = get_jwt_identity() or 'IT-2026-NP'
    student = Student.query.filter_by(student_id=current_user_id).first()
    if student:
        return jsonify(student.onboarding_status)
    return jsonify({"documents": False, "fees": False, "registration": False})

@app.route('/api/update-onboarding', methods=['POST'])
@jwt_required(optional=True)
def update_onboarding():
    try:
        current_user_id = get_jwt_identity() or 'IT-2026-NP'
        data = request.get_json()
        status = data.get("status")

        student = Student.query.filter_by(student_id=current_user_id).first()
        if student:
            student.onboarding_status = status
            db.session.commit()
            return jsonify({"success": True})
            
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print("UPDATE ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/admin/stats')
def get_admin_stats():
    try:
        total = Student.query.count()
        students = Student.query.all()
        
        enrolled = 0
        pending_fees = 0
        pending_docs = 0

        for s in students:
            st = s.onboarding_status
            if st.get("documents") and st.get("fees") and st.get("registration"):
                enrolled += 1
            if not st.get("fees"):
                pending_fees += 1
            if not st.get("documents"):
                pending_docs += 1

        return jsonify({
            "total_students": total,
            "enrolled": enrolled,
            "pending_fees": pending_fees,
            "pending_docs": pending_docs,
            "high_risk_alerts": pending_fees
        })

    except Exception as e:
        print("STATS ERROR:", e)
        return jsonify({
            "total_students": 0,
            "enrolled": 0,
            "pending_fees": 0,
            "pending_docs": 0,
            "high_risk_alerts": 0
        })

@app.route('/chat', methods=['POST'])
@jwt_required(optional=True)
def chat():
    current_user_id = get_jwt_identity() or 'IT-2026-NP'
    
    student = Student.query.filter_by(student_id=current_user_id).first()
    if not student:
        return jsonify({
            "message": "User context not found.",
            "status": {
                "documents": False,
                "fees": False,
                "registration": False
            }
        })

    data = request.get_json()
    user_message = data.get("message", "")

    try:
        from backend.agent.agent import AdmitAssistAgent
        agent = AdmitAssistAgent()

        # 🔥 agent returns ONLY message
        reply = agent.run(user_message, current_user_id)

        # 🔥 refresh DB state
        db.session.refresh(student)

        # 🔥 ALWAYS send structured response
        return jsonify({
            "message": reply,
            "status": {
                "documents": student.onboarding_status.get("doc", False),
                "fees": student.onboarding_status.get("fees", False),
                "registration": student.onboarding_status.get("registration", False)
            }
        })

    except Exception as e:
        print("Agent Error:", e)

        return jsonify({
            "message": "Something went wrong. Please try again.",
            "status": {
                "documents": student.onboarding_status.get("doc", False),
                "fees": student.onboarding_status.get("fees", False),
                "registration": student.onboarding_status.get("registration", False)
            }
        })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)