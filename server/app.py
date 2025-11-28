from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# 安全密钥，防止别人恶意提交数据
SECRET_KEY = "my_secret_password"

# 用于存储服务器状态的内存字典 (实际生产环境建议用 Redis 或 SQLite)
# 格式: {'server_name': {'cpu': 10, 'ram': 50, 'last_updated': timestamp}}
servers_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    key = data.get('auth')
    
    if key != SECRET_KEY:
        return jsonify({"status": "error", "message": "Invalid Token"}), 403
    
    name = data.get('name')
    servers_status[name] = {
        'cpu': data.get('cpu'),
        'ram': data.get('ram'),
        'disk': data.get('disk'),
        'last_updated': time.time()
    }
    return jsonify({"status": "success"})

@app.route('/api/stats')
def stats():
    # 移除超时的服务器 (例如超过 10 秒没上报的)
    current_time = time.time()
    active_servers = {}
    
    for name, data in servers_status.items():
        if current_time - data['last_updated'] < 10:
            active_servers[name] = data
        else:
            # 标记为离线
            data['cpu'] = 0
            data['status'] = 'offline'
            active_servers[name] = data
            
    return jsonify(active_servers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
