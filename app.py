from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send
import os, json, re, string
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = 'secret123'  # нужна для session
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/mode', methods=['POST'])
def mode_select():
    mode = request.form['mode']
    session['mode'] = mode
    submodes = {
        "1.1": "Система загадывает число, пользователь задаёт вопросы",
        "1.2": "Система задаёт вопросы пользователю",
        "2.1": "Один игрок загадывает число, другой задаёт вопросы",
        "2.2": "Игроки по очереди играют"
    }
    submodes = {k: v for k, v in submodes.items() if k.startswith("1") if mode == "computer" else k.startswith("2")}
    return render_template('mode_select.html', submodes=submodes)

@app.route('/room', methods=['POST'])
def room_setup():
    session['submode'] = request.form['submode']
    return render_template('room_setup.html')

@app.route('/game', methods=['POST'])
def game():
    session['room_code'] = request.form['room_code']
    session['action'] = request.form['action']
    return render_template('game.html', submode=session['submode'], room_code=session['room_code'])

@socketio.on('message')
def handle_message(msg):
    print("Сообщение:", msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
