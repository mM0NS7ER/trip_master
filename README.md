# Trip Master - AI旅行规划师(开发中)

Trip Master是一个基于AI技术的智能旅行规划平台，旨在简化用户的旅行规划过程，提供个性化的行程安排、预算管理和实时辅助功能。

## 项目概述

Trip Master通过AI技术，提供一个集行程生成、预算管理、实时辅助于一体的智能旅行规划平台，简化用户决策流程，提升旅行体验。

## 核心功能

- **智能对话交互**：用户可通过文本或语音与AI交互，描述旅行需求
- **行程可视化**：在地图上展示行程路线和关键点位（POI）
- **行程管理**：支持手动调整行程顺序，增删景点
- **预算管理**：实时计算并显示行程总花费，支持分项预算设置
- **多设备同步**：用户登录后，行程数据在手机、平板、电脑间同步

## 技术架构

### 前端技术栈
- **框架**：React + TypeScript
- **构建工具**：Vite
- **样式**：Tailwind CSS + Shadcn/UI组件库
- **地图集成**：高德地图API
- **路由**：React Router DOM
- **状态管理**：Zustand（轻量级状态管理）

### 后端技术栈
- **主框架**：Python + FastAPI
- **数据库**：PostgreSQL（主数据）+ Redis（缓存），使用Supabase BaaS平台
- **ORM**：SQLAlchemy
- **数据库迁移**：Alembic
- **认证**：JWT（JSON Web Tokens）
- **文件存储**：OSS云存储（行程附件、用户头像）

### 第三方服务集成
- **地图服务**：高德地图Web API（路径规划、POI搜索、静态地图）
- **AI大模型**：DeepSeek API
- **语音服务**：科大讯飞语音识别+合成API

## 项目结构

```
trip_master/
├── frontend/                # 前端项目
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   │   ├── ChatArea/   # 聊天区域组件
│   │   │   │   ├── ChatArea.tsx      # 聊天主体
│   │   │   │   ├── InputSection.tsx  # 输入区域
│   │   │   │   └── WelcomeSection.tsx # 欢迎区域
│   │   │   ├── ui/         # 基础UI组件
│   │   │   │   ├── button.tsx        # 按钮组件
│   │   │   │   ├── dialog.tsx        # 对话框组件
│   │   │   │   ├── dropdown-menu.tsx # 下拉菜单组件
│   │   │   │   ├── input.tsx         # 输入框组件
│   │   │   │   └── label.tsx         # 标签组件
│   │   │   ├── AuthModal.tsx  # 认证模态框
│   │   │   ├── ChatLayout.tsx # 聊天布局
│   │   │   ├── Header.tsx      # 页头组件
│   │   │   ├── History.tsx     # 历史记录
│   │   │   ├── MapArea.tsx     # 地图区域
│   │   │   ├── Sidebar.tsx     # 侧边栏
│   │   │   └── UserProfile.tsx # 用户资料
│   │   ├── store/           # 状态管理
│   │   │   └── authStore.tsx  # 认证状态
│   │   ├── App.tsx          # 主组件
│   │   ├── main.tsx         # 入口文件
│   │   └── index.css        # 全局样式
│   ├── index.html           # HTML模板
│   ├── package.json         # 依赖配置
│   ├── vite.config.ts       # Vite配置
│   ├── tailwind.config.js   # Tailwind配置
│   ├── tsconfig.json        # TypeScript配置
│   └── postcss.config.js    # PostCSS配置
└── README.md                # 项目说明
```

## 快速开始

### 前端

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 构建生产版本：
```bash
npm run build
```

### 后端

1. 进入后端目录：
```bash
cd backend
```

2. 创建并激活Python虚拟环境：
```bash
# 创建虚拟环境
conda create -n trip-master python=3.12
conda activate trip-master

# Linux/Mac激活虚拟环境
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
# 创建环境变量文件
touch .env

# 编辑.env文件，填入必要的API密钥和配置
```

5. 运行数据库迁移（如需要）：
```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

6. 启动开发服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. 构建生产版本（使用Docker）：
```bash
# 构建Docker镜像
docker build -t trip-master-backend .

# 运行容器
docker run -p 8000:8000 trip-master-backend
```

#### 后端API文档

启动后端服务后，可以通过以下地址访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

#### 后端项目结构

```
backend/
├── app/                   # 应用源代码
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
├── alembic/               # 数据库迁移
├── .env                   # 环境变量
├── requirements.txt       # 依赖配置
└── Dockerfile             # Docker配置
```

## 开发规范

- 代码严格遵循单一职责原则
- 所有组件使用TypeScript编写
- 样式使用Tailwind CSS
- 提交前运行lint检查代码质量

## 联系方式

如有问题或建议，请联系开发团队。
