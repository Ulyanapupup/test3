import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send
import json, re, string, os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Загадано число
secret_number = 17

def is_greater(x): return secret_number > x
def is_less(x): return secret_number < x
def is_equal(x): return secret_number == x
def is_prime(_=None):
    if secret_number < 2: return False
    for i in range(2, int(secret_number ** 0.5) + 1):
        if secret_number % i == 0: return False
    return True

question_functions = {
    "is_greater": is_greater,
    "is_less": is_less,
    "is_equal": is_equal,
    "is_prime": is_prime
}

with open('questions.json', 'r', encoding='utf-8') as f:
    question_map = json.load(f)

def process_question(q):
    q = q.lower().translate(str.maketrans('', '', string.punctuation))
    for keyword, func_name in question_map.items():
        if keyword in q:
            func = question_functions[func_name]
            if func_name == "is_prime":
                return "Да" if func() else "Нет"
            nums = re.findall(r'\d+', q)
            if not nums: return "Пожалуйста, укажите число"
            return "Да" if func(int(nums[0])) else "Нет"
    return "Неизвестный вопрос"

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/room_setup')
def room_setup():
    return render_template('room_setup.html')

@app.route('/game/<mode>')
def game_mode(mode):
    return render_template('game_mode.html', mode=mode)
    
@app.route('/game')
def game():
    room_code = request.args.get('room')
    if not room_code:
        return "Ошибка: не указан код комнаты", 400
    # Передаем код комнаты в шаблон, чтобы использовать в JS для WebSocket и логики
    return render_template('game.html', room_code=room_code)


@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get("question", "")
    answer = process_question(question)
    return jsonify({"answer": answer})

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
