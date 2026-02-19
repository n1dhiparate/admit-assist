from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os
import requests
import psycopg2
from psycopg2.extras import Json
from backend.rag import retrieve_context

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Load API key and Database URL
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ----------------------------
# Database Helper Function
# ----------------------------
def sync_to_db(status):
    """Saves the current onboarding status to PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET onboarding_status = %s WHERE student_id = 'IT-2026-NP'",
            (Json(status),)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database sync error: {e}")

onboarding_status = {
    "doc": False, "fee": False, "reg": False, "hostel": False, "lms": False
}

# ----------------------------
# NEW: Seed Database Route (DO NOT DELETE EXISTING CODE)
# ----------------------------
@app.route('/admin/seed', methods=['POST'])
def seed_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("DELETE FROM students;")

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

            cur.execute(
                "INSERT INTO students (student_id, name, onboarding_status) VALUES (%s, %s, %s)",
                (s_id, s_name, Json(status))
            )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("SEED ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ... [Keep your existing chat and get_onboarding routes exactly as they are]
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/get-onboarding', methods=['GET'])
def get_onboarding():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT onboarding_status FROM students WHERE student_id = 'IT-2026-NP'")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(result[0] if result else onboarding_status)
    except:
        return jsonify(onboarding_status)


@app.route('/api/update-onboarding', methods=['POST'])
def update_onboarding():
    try:
        data = request.get_json()
        status = data.get("status")

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET onboarding_status = %s WHERE student_id = 'IT-2026-NP'",
            (Json(status),)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        print("UPDATE ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/admin/stats')
def get_admin_stats():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Total students
        cur.execute("SELECT COUNT(*) FROM students;")
        total = cur.fetchone()[0]

        # Fully completed onboarding
        cur.execute("""
            SELECT COUNT(*) FROM students
            WHERE 
                (onboarding_status->>'doc')::boolean = true AND
                (onboarding_status->>'fee')::boolean = true AND
                (onboarding_status->>'reg')::boolean = true AND
                (onboarding_status->>'hostel')::boolean = true AND
                (onboarding_status->>'lms')::boolean = true;
        """)
        enrolled = cur.fetchone()[0]

        # Pending fees
        cur.execute("""
            SELECT COUNT(*) FROM students
            WHERE (onboarding_status->>'fee')::boolean = false;
        """)
        pending_fees = cur.fetchone()[0]

        # Pending docs
        cur.execute("""
            SELECT COUNT(*) FROM students
            WHERE (onboarding_status->>'doc')::boolean = false;
        """)
        pending_docs = cur.fetchone()[0]

        cur.close()
        conn.close()

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
def chat():
    global onboarding_status
    data = request.get_json()
    user_message = data.get("message", "")
    message = user_message.lower()

    updated = False
    if "document" in message and ("complete" in message or "verified" in message):
        onboarding_status["doc"] = True
        updated = True
    if "fee" in message and ("paid" in message or "done" in message):
        onboarding_status["fee"] = True
        updated = True
    if "register" in message and "course" in message:
        onboarding_status["reg"] = True
        updated = True

    if updated:
        sync_to_db(onboarding_status)

    context = retrieve_context(user_message)
    
    # ✅ REVERTED TO YOUR ORIGINAL URL STRUCTURE
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt_text = f"Context: {context}\n\nQuestion: {user_message}"
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": reply, "status": onboarding_status, "source": "Admission Brochure"})
        return jsonify({"reply": context or "API Error", "status": onboarding_status})
    except:
        return jsonify({"reply": context or "Error", "status": onboarding_status})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)