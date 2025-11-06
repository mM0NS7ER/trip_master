
# Trip Master - AI旅行规划师前端

这是一个基于React的AI旅行规划师前端应用，提供智能旅行规划、地图展示和聊天交互功能。

## 技术栈

- **框架**: Vite + React (TypeScript)
- **样式**: Tailwind CSS + Shadcn/UI
- **路由**: React Router DOM
- **地图**: 高德地图 JavaScript API
- **图标**: Lucide React

## 功能特点

- 智能聊天交互界面
- 高德地图集成与展示
- 会话历史记录管理
- 响应式布局设计

## 安装与运行

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 项目结构

```
src/
  components/
    Header.tsx          # 顶部栏
    Sidebar.tsx         # 左侧导航栏
    History.tsx         # 历史会话侧边栏
    ChatArea/           # 聊天区
      WelcomeSection.tsx
      InputSection.tsx
      ChatArea.tsx
    MapArea.tsx         # 地图区
    ChatLayout.tsx      # 聊天页面布局
  lib/
    utils.ts            # 工具函数
  App.tsx               # 主组件，处理路由
  main.tsx              # 入口文件
```

## 开发说明

- 所有后端交互目前使用前端模拟，标记了`// TODO: Integrate backend API`
- 会话ID自动生成并持久化到localStorage
- 地图使用高德地图JavaScript API，测试密钥已集成

## 联系方式

如有问题或建议，请联系开发团队。
