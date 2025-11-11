# 使用多阶段构建
# 前端构建阶段
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端 package.json 和 package-lock.json
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源代码
COPY frontend/ .

# 构建前端应用
RUN npm run build:prod

# 后端构建阶段
FROM python:3.11-slim AS backend

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt .

# 安装后端 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端应用代码
COPY backend/ .

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# 复制 Nginx 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default

# 暴露端口
EXPOSE 80 8000

# 复制启动脚本
COPY docker/start.sh /start.sh
# 确保使用 Unix 风格的换行符
RUN sed -i 's/\r$//' /start.sh && chmod +x /start.sh

# 复制环境变量示例文件
COPY backend/.env.example /app/.env.example

# 启动命令
CMD ["/start.sh"]
