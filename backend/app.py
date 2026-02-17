from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)


# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ GLOBAL ONBOARDING STATUS (outside functions)
onboarding_status = {
    "document_verification": False,
    "fee_payment": False,
    "course_registration": False,
    "hostel_allocation": False,
    "lms_onboarding": False
}
 

# Serve frontend
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Status endpoint
@app.route('/status')
def get_status():
    return jsonify(onboarding_status)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    global onboarding_status

    data = request.get_json()
    user_message = data.get("message", "")
    message = user_message.lower()

    print("USER MESSAGE:", user_message)

    # ✅ Rule-based onboarding updates

    if "admission" in message:
     return jsonify({
        "reply": (
            "🎓 Congratulations on your admission!\n\n"
            "Here are your onboarding steps:\n\n"
            "1️⃣ Complete document verification\n"
            "2️⃣ Pay semester fees\n"
            "3️⃣ Register for courses\n"
            "4️⃣ Apply for hostel (if required)\n"
            "5️⃣ Complete LMS onboarding\n\n"
            "You can tell me once you complete a step, and I’ll update your progress."
        )
    })

    if "document" in message and "complete" in message:
        onboarding_status["document_verification"] = True

    if "fee" in message and "paid" in message:
        onboarding_status["fee_payment"] = True

    if "register" in message and "course" in message:
        onboarding_status["course_registration"] = True

    if "hostel" in message and "allot" in message:
        onboarding_status["hostel_allocation"] = True

    if "lms" in message and "setup" in message:
        onboarding_status["lms_onboarding"] = True

    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        print("GEMINI RESPONSE:", result)

        if "error" in result:
            return jsonify({
                "reply": "⚠️ API quota exceeded. Please try again later."
            })

        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": reply})

        return jsonify({"reply": "Unexpected response from Gemini."})
    
    

    except Exception as e:
        return jsonify({"reply": f"Server error: {str(e)}"}), 500
    
   




if __name__ == '__main__':
    app.run(debug=True)
