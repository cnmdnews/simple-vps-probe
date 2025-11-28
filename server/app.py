from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import time
from collections import deque  # 【新增】用于存储历史数据

app = Flask(__name__)

# ================= 配置区 =================
app.config['SECRET_KEY'] = 'change_this_to_a_very_long_random_string'
PROBE_SECRET_KEY = "my_secret_password"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 
# =========================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USERNAME:
        return User(user_id)
    return None

# 【修改】servers_status 结构说明：
# {
#   'server_name': {
#       'cpu': 10, 'ram': 50, ..., 
#       'history': deque([...], maxlen=60)  <-- 新增历史记录
#   }
# }
servers_status = {}

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    if data.get('auth') != PROBE_SECRET_KEY:
        return jsonify({"status": "error", "message": "Invalid Token"}), 403
    
    name = data.get('name')
    now_str = time.strftime('%H:%M:%S')

    # 如果是新服务器，初始化结构
    if name not in servers_status:
        servers_status[name] = {
            'history': deque(maxlen=60) # 最多保存60个点
        }
    
    # 更新当前状态
    servers_status[name].update({
        'cpu': data.get('cpu'),
        'ram': data.get('ram'),
        'disk': data.get('disk'),
        'last_updated': time.time(),
        'status': 'online'
    })

    # 【新增】追加历史数据
    servers_status[name]['history'].append({
        'time': now_str,
        'cpu': data.get('cpu'),
        'ram': data.get('ram'),
        'disk': data.get('disk')
    })

    return jsonify({"status": "success"})

@app.route('/api/stats')
@login_required
def stats():
    now = time.time()
    response_data = {}
    
    for name, data in servers_status.items():
        # 检查离线
        if now - data['last_updated'] > 15:
            data['status'] = 'offline'
        
        # 【关键】deque 对象无法直接 JSON 化，需要转成 list
        # 我们复制一份数据用于返回，避免修改原始数据
        server_info = data.copy()
        server_info['history'] = list(data['history']) 
        response_data[name] = server_info

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
