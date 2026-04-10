from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os
import requests
from backend.rag import retrieve_context
from groq import Groq

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
                "doc": random.choice([True, False]),
                "fee": random.choice([True, False]),
                "reg": random.choice([True, False]),
                "hostel": random.choice([True, False]),
                "lms": random.choice([True, False])
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
    return jsonify({"doc": False, "fee": False, "reg": False, "hostel": False, "lms": False})

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
            if st.get("doc") and st.get("fee") and st.get("reg") and st.get("hostel") and st.get("lms"):
                enrolled += 1
            if not st.get("fee"):
                pending_fees += 1
            if not st.get("doc"):
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
        return jsonify({"reply": "User context not found.", "status": None})

    data = request.get_json()
    user_message = data.get("message", "")
    message = user_message.lower()

    updated = False
    status = student.onboarding_status.copy() # important: copy so SQLAlchemy detects mutation

    if "document" in message and ("complete" in message or "verified" in message):
        status["doc"] = True
        updated = True
    if "fee" in message and ("paid" in message or "done" in message):
        status["fee"] = True
        updated = True
    if "register" in message and "course" in message:
        status["reg"] = True
        updated = True

    if updated:
        student.onboarding_status = status
        db.session.commit()

    context = retrieve_context(user_message)
    
    final_prompt = f"""
You are Admit-Assist.
Answer ONLY from CONTEXT.
Return answer in this exact format:
<Short Answer>
Source: Official Admission Brochure
Do not add anything else.

CONTEXT:
{context}

QUESTION:
{user_message}
"""
    
    try:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({"reply": "Please set GROQ_API_KEY in .env file.", "status": student.onboarding_status})

        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": final_prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        reply = chat_completion.choices[0].message.content
        return jsonify({"reply": reply, "status": student.onboarding_status, "source": "Admission Brochure"})
    except Exception as e:
        print(f"Groq API Error: {e}")
        return jsonify({"reply": "I could not find this information in the admission brochure.", "status": student.onboarding_status})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)