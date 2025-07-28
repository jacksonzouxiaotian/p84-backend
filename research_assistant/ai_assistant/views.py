import os
from flask import Blueprint, jsonify, request
import google.generativeai as genai

blueprint = Blueprint("ai", __name__, url_prefix="/ai")

# 设置 Google AI Key（来自 .env）
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 使用 Gemini 模型
model = genai.GenerativeModel("gemini-pro")

@blueprint.route("/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    try:
        response = model.generate_content(question)
        answer = response.text.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
