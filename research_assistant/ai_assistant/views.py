import os
import openai
from flask import Blueprint, request, jsonify

blueprint = Blueprint("ai", __name__, url_prefix="/ai")

# 设置 OpenAI API Key（建议通过环境变量或配置文件）
openai.api_key = os.getenv("OPENAI_API_KEY")

@blueprint.route("/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或 gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
