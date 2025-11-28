# Simple VPS Probe (简易探针)

这是一个基于 Python Flask 和 Psutil 开发的轻量级服务器监控探针。

监控端一键脚本：
wget -O install.sh https://raw.githubusercontent.com/cnmdnews/simple-vps-probe/main/install.sh && chmod +x install.sh && bash install.sh

被控端一键脚本：
wget -O agent.sh https://raw.githubusercontent.com/cnmdnews/simple-vps-probe/main/install_agent.sh && chmod +x agent.sh && bash agent.sh

## 功能
- 实时监控 CPU、内存、硬盘使用率
- 简单的 Web 面板展示
- 支持多台服务器监控

## 使用方法

### 服务端 (Dashboard)
1. 进入 `server` 目录
2. 安装依赖: `pip install -r requirements.txt`
3. 运行: `python app.py`
4. 访问 `http://localhost:5000`

### 客户端 (Agent)
1. 进入 `agent` 目录
2. 修改 `client.py` 中的 `SERVER_URL` 为你的服务端地址
3. 安装依赖: `pip install -r requirements.txt`
4. 运行: `python client.py`

## 协议
MIT License
