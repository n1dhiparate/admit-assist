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


# Serve frontend
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    print("USER MESSAGE:", user_message)

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

        # 🔴 Handle API errors (quota, etc.)
        if "error" in result:
            return jsonify({
                "reply": "⚠️ API quota exceeded. Please try again later.In production, this is powered by Gemini."
            })

        # 🟢 Normal success case
        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": reply})

        # 🟡 Unexpected structure fallback
        return jsonify({"reply": "Unexpected response from Gemini."})

    except Exception as e:
        return jsonify({"reply": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
