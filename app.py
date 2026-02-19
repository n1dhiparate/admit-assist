from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
from backend.rag import retrieve_context

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Load API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# ----------------------------
# Onboarding progress tracker
# ----------------------------
onboarding_status = {
    "doc": False,
    "fee": False,
    "reg": False,
    "hostel": False,
    "lms": False
}

# ----------------------------
# Serve frontend
# ----------------------------
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# ----------------------------
# Status Route
# ----------------------------
@app.route('/status')
def get_status():
    return jsonify(onboarding_status)

# ----------------------------
# Admin Dashboard Stats
# ----------------------------
@app.route('/admin/stats')
def get_admin_stats():
    return jsonify({
        "total_students": 120,
        "enrolled": 82,
        "pending_fees": 14,
        "pending_docs": 9,
        "high_risk_alerts": 6
    })

# ----------------------------
# Chat Route (Gemini + RAG)
# ----------------------------
@app.route('/chat', methods=['POST'])
def chat():
    global onboarding_status

    data = request.get_json()
    user_message = data.get("message", "")
    message = user_message.lower()

    # Rule-based onboarding updates
    if "document" in message and ("complete" in message or "verified" in message):
        onboarding_status["doc"] = True

    if "fee" in message and ("paid" in message or "done" in message):
        onboarding_status["fee"] = True

    if "register" in message and "course" in message:
        onboarding_status["reg"] = True

    # RAG retrieval
    context = retrieve_context(user_message)

    if not context:
        return jsonify({
            "reply": "I do not have official information about this in the brochure.",
            "status": onboarding_status
        })

    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        prompt_text = f"""
You are Admit-Assist, a responsible AI onboarding assistant.
Answer ONLY using the official admission brochure context below.

Context:
{context}

User Question:
{user_message}
"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }

        response = requests.post(url, json=payload)

        # 🔒 Safe fallback if Gemini fails
        if response.status_code != 200:
            return jsonify({
                "reply": context,  # fallback to RAG directly
                "status": onboarding_status,
                "source": "Admission Brochure"
            })

        result = response.json()

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({
            "reply": reply,
            "status": onboarding_status,
            "source": "Admission Brochure"
        })

    except Exception:
        return jsonify({
            "reply": context,  # fallback again
            "status": onboarding_status,
            "source": "Admission Brochure"
        })


# ----------------------------
# Run Server
# ----------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
