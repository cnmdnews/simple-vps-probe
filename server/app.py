from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import time

app = Flask(__name__)

# ================= 配置区 =================
# 1. 修改 SECRET_KEY (用于加密会话，随便乱打一串字母数字)
app.config['SECRET_KEY'] = 'change_this_to_a_very_long_random_string'

# 2. 修改探针通讯密钥 (Agent连接用)
PROBE_SECRET_KEY = "my_secret_password"

# 3. 配置管理员账号 (为了演示方便，这里直接写死在代码里)
# 在生产环境中，应该使用数据库并在存储前对密码进行哈希加密
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 
# =========================================

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # 未登录时自动跳转的视图名

# 模拟的用户数据库和简单的用户类
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USERNAME:
        return User(user_id)
    return None

# 内存中存储服务器状态
servers_status = {}

# --- 页面路由 ---

@app.route('/')
@login_required  # 【关键】加了这个装饰器，只有登录才能访问
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 简单的用户名密码比对
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

# --- API 接口 (供 Agent 调用) ---

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    # 校验探针密钥
    if data.get('auth') != PROBE_SECRET_KEY:
        return jsonify({"status": "error", "message": "Invalid Token"}), 403
    
    name = data.get('name')
    servers_status[name] = {
        'cpu': data.get('cpu'),
        'ram': data.get('ram'),
        'disk': data.get('disk'),
        'last_updated': time.time(),
        'status': 'online'
    }
    return jsonify({"status": "success"})

@app.route('/api/stats')
@login_required # API 也需要登录才能查看，防止泄露
def stats():
    now = time.time()
    # 检查是否有离线服务器 (超过15秒没上报则视为离线)
    for name, data in servers_status.items():
        if now - data['last_updated'] > 15:
            data['status'] = 'offline'
            # 离线时保留最后的数据，但状态标记为离线
    return jsonify(servers_status)

if __name__ == '__main__':
    # 如果使用 Nginx 反代，这里 host 改为 '127.0.0.1'
    app.run(host='0.0.0.0', port=5000)
