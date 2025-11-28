import psutil
import requests
import time
import socket

# 配置
SERVER_URL = "http://127.0.0.1:5000/api/report" # 部署时请改为你服务端的真实IP/域名
SECRET_KEY = "my_secret_password"
SERVER_NAME = socket.gethostname() # 自动获取主机名，也可以手动指定

def get_stats():
    # 获取 CPU 使用率
    cpu = psutil.cpu_percent(interval=1)
    # 获取 内存 使用率
    ram = psutil.virtual_memory().percent
    # 获取 硬盘 使用率
    disk = psutil.disk_usage('/').percent
    
    return {
        "name": SERVER_NAME,
        "auth": SECRET_KEY,
        "cpu": cpu,
        "ram": ram,
        "disk": disk
    }

def main():
    print(f"探针启动: {SERVER_NAME}")
    while True:
        try:
            data = get_stats()
            requests.post(SERVER_URL, json=data, timeout=5)
            print(f"数据已发送: CPU {data['cpu']}%")
        except Exception as e:
            print(f"连接服务器失败: {e}")
        
        time.sleep(2) # 每2秒上报一次

if __name__ == "__main__":
    main()
