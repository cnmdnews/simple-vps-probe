#!/bin/bash

# =================配置区=================
# ⚠️ 请将下面的 cenvvv 换成你的 GitHub 用户名
GITHUB_REPO_URL="https://github.com/cnmdnews/simple-vps-probe.git"
INSTALL_DIR="/opt/simple-vps-probe-agent"
# =======================================

# 颜色定义
GREEN="\033[32m"
RED="\033[31m"
PLAIN="\033[0m"

echo -e "${GREEN}=== 开始安装 VPS 探针客户端 (Agent) ===${PLAIN}"

# 1. 检查 root 权限
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}错误: 请使用 root 权限运行此脚本 (输入 sudo -i)${PLAIN}" 
   exit 1
fi

# 2. 交互式输入服务端信息
echo -e ""
read -p "请输入服务端(面板)的 IP 地址: " SERVER_IP
if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}错误: IP 地址不能为空${PLAIN}"
    exit 1
fi

read -p "请输入服务端端口 (默认 5000): " SERVER_PORT
SERVER_PORT=${SERVER_PORT:-5000} # 如果没输，默认5000

echo -e "${GREEN}即将连接到 -> http://$SERVER_IP:$SERVER_PORT${PLAIN}"
echo -e ""

# 3. 安装依赖
echo -e "${GREEN}正在安装系统依赖...${PLAIN}"
apt-get update -y
apt-get install git python3 python3-pip python3-venv -y

# 4. 拉取代码
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

echo -e "${GREEN}正在拉取代码...${PLAIN}"
git clone $GITHUB_REPO_URL $INSTALL_DIR

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}错误: 代码拉取失败，请检查 GitHub 地址。${PLAIN}"
    exit 1
fi

# 5. 配置 Python 环境
echo -e "${GREEN}配置 Python 虚拟环境...${PLAIN}"
cd $INSTALL_DIR/agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 【关键】修改代码中的 Server 地址
# 使用 sed 命令将默认的 127.0.0.1 替换为用户输入的 IP
echo -e "${GREEN}正在修改配置文件...${PLAIN}"
sed -i "s|http://127.0.0.1:5000|http://${SERVER_IP}:${SERVER_PORT}|g" client.py

# 7. 配置 Systemd 开机自启
echo -e "${GREEN}配置系统服务...${PLAIN}"
cat > /etc/systemd/system/vpsagent.service <<EOF
[Unit]
Description=VPS Probe Agent
After=network.target

[Service]
User=root
WorkingDirectory=$INSTALL_DIR/agent
ExecStart=$INSTALL_DIR/agent/venv/bin/python client.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 8. 启动
systemctl daemon-reload
systemctl enable vpsagent
systemctl restart vpsagent

echo -e ""
echo -e "${GREEN}=========================================${PLAIN}"
echo -e "${GREEN} 客户端安装成功！数据已开始上报 ${PLAIN}"
echo -e "${GREEN}=========================================${PLAIN}"
echo -e "请回到服务端网页查看是否出现本机信息。"
echo -e "管理命令: systemctl [status|restart|stop] vpsagent"
echo -e "${GREEN}=========================================${PLAIN}"
