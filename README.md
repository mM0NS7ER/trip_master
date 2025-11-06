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
- **主框架**：Node.js + Express.js
- **AI模型**：DeepSeek
- **数据库**：PostgreSQL（主数据）+ Redis（缓存），使用Supabase BaaS平台
- **认证**：NextAuth.js（支持Google、微信等第三方登录）
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
│   │   ├── lib/           # 工具函数
│   │   ├── App.tsx        # 主组件
│   │   └── main.tsx       # 入口文件
│   ├── package.json       # 依赖配置
│   └── vite.config.ts     # Vite配置
└── README.md               # 项目说明
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

## 开发规范

- 代码严格遵循单一职责原则
- 所有组件使用TypeScript编写
- 样式使用Tailwind CSS
- 提交前运行lint检查代码质量

## 联系方式

如有问题或建议，请联系开发团队。
