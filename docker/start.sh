#!/bin/bash

# 检查 .env 文件是否存在，如果不存在则从示例文件复制
if [ ! -f /app/.env ]; then
    echo "未找到 .env 文件，从 .env.example 创建模板文件..."
    cp /app/.env.example /app/.env
    echo "请编辑 /app/.env 文件，填入您的实际配置值后重启容器。"
    echo "您可以使用以下命令挂载您的配置文件："
    echo "docker run -p 80:80 -p 8000:8000 -v /path/to/your/.env:/app/.env trip-master"
    exit 1
fi

# 启动 Nginx（在后台运行）
nginx &

# 启动后端服务（在前台运行）
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000
