#!/bin/bash

# =================配置区=================
# ⚠️⚠️⚠️ 请将下面的 username 换成你的 GitHub 用户名
GITHUB_REPO_URL="https://github.com/cnmdnews/simple-vps-probe.git"
INSTALL_DIR="/opt/simple-vps-probe"
PORT=5000
# =======================================

# 颜色定义
GREEN="\033[32m"
RED="\033[31m"
PLAIN="\033[0m"

echo -e "${GREEN}=== 开始安装 VPS 探针服务端 ===${PLAIN}"

# 1. 检查是否为 root 用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}错误: 请使用 root 权限运行此脚本 (输入 sudo -i)${PLAIN}" 
   exit 1
fi

# 2. 安装基础依赖 (Git, Python3, Pip)
echo -e "${GREEN}正在更新系统并安装依赖...${PLAIN}"
apt-get update -y
apt-get install git python3 python3-pip python3-venv -y

# 3. 拉取代码
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}目录已存在，正在删除旧文件...${PLAIN}"
    rm -rf "$INSTALL_DIR"
fi

echo -e "${GREEN}正在从 GitHub 拉取代码...${PLAIN}"
git clone $GITHUB_REPO_URL $INSTALL_DIR

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}错误: 代码拉取失败，请检查 GitHub 地址是否正确。${PLAIN}"
    exit 1
fi

# 4. 设置 Python 虚拟环境并安装依赖
echo -e "${GREEN}正在配置 Python 环境...${PLAIN}"
cd $INSTALL_DIR/server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. 配置 Systemd 守护进程 (开机自启)
echo -e "${GREEN}正在配置系统服务 (Systemd)...${PLAIN}"
cat > /etc/systemd/system/vpsprobe.service <<EOF
[Unit]
Description=VPS Probe Server
After=network.target

[Service]
User=root
WorkingDirectory=$INSTALL_DIR/server
ExecStart=$INSTALL_DIR/server/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. 启动服务
systemctl daemon-reload
systemctl enable vpsprobe
systemctl restart vpsprobe

# 7. 放行防火墙端口 (如果有 ufw)
if command -v ufw > /dev/null; then
    ufw allow $PORT/tcp
    echo -e "${GREEN}已放行 $PORT 端口${PLAIN}"
fi

# 8. 获取本机 IP 并输出结果
IPV4=$(curl -s4m8 ip.sb)
echo -e ""
echo -e "${GREEN}=========================================${PLAIN}"
echo -e "${GREEN} 安装成功！服务已启动 ${PLAIN}"
echo -e "${GREEN}=========================================${PLAIN}"
echo -e "访问地址: http://$IPV4:$PORT"
echo -e "管理命令: systemctl [start|stop|restart] vpsprobe"
echo -e "${GREEN}=========================================${PLAIN}"
