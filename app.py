from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import json
import os

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

DATA_FILE = 'users.json'

# 初始化用户数据文件
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_users()
    if any(user['username'] == username for user in users):
        return jsonify({'message': '用户名已存在'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    users.append({'username': username, 'password': hashed_pw})
    save_users(users)

    return jsonify({'message': '注册成功'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_users()
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': '密码错误'}), 401

    return jsonify({'message': '登录成功'}), 200

if __name__ == '__main__':
    app.run(debug=True)
