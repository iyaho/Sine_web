import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
import database

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
bcrypt = Bcrypt(app)

LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
login_attempts = {}  # {username: {'count': int, 'locked_until': datetime|None}}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.generate_password_hash(password)

        try:
            conn = database.get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='이미 존재하는 아이디예요.')

@app.route('/check-username')
def check_username():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'available': None})
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    return jsonify({'available': not exists})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 잠금 여부 확인
        info = login_attempts.get(username, {'count': 0, 'locked_until': None})
        if info['locked_until'] and datetime.now() < info['locked_until']:
            secs = (info['locked_until'] - datetime.now()).seconds
            mins = secs // 60 + 1
            return render_template('login.html', error=f'로그인 시도 횟수를 초과했습니다. {mins}분 후에 다시 시도해주세요.')

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            login_attempts.pop(username, None)
            session['username'] = username
            return redirect(url_for('profile'))

        # 실패 처리
        if username not in login_attempts:
            login_attempts[username] = {'count': 0, 'locked_until': None}
        login_attempts[username]['count'] += 1

        if login_attempts[username]['count'] >= LOCKOUT_ATTEMPTS:
            login_attempts[username]['locked_until'] = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
            login_attempts[username]['count'] = 0
            return render_template('login.html', error=f'로그인 시도 횟수를 초과했습니다. {LOCKOUT_MINUTES}분 후에 다시 시도해주세요.')

        return render_template('login.html', error='아이디 또는 비밀번호가 틀렸어요.')

@app.route('/profile')
def profile():
    if session.get('username') is None:
        return redirect(url_for('login'))

    username = session.get('username')
    return render_template('profile.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True)
