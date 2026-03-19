# FactorFlow Frontend - React + Ant Design

## 📋 项目概述

FactorFlow 量化因子分析平台前端 - 使用 React + TypeScript + Ant Design 构建

## 🚀 快速开始

### 1. 安装依赖

```bash
cd f:/pythonproject/FactorFlow/frontend/react-antd

# 核心依赖
npm install antd react-router-dom axios

# 图标库  
npm install @ant-design/icons

# 其他工具
npm install dayjs
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

## 📁 项目结构

```
react-antd/
├── src/
│   ├── pages/              # 页面组件
│   │   ├── Home.tsx        # 首页 (已完成)
│   │   ├── FactorManagement.tsx
│   │   ├── FactorMining.tsx
│   │   ├── PortfolioAnalysis.tsx
│   │   └── Backtesting.tsx
│   ├── services/           # API 服务
│   │   └── api.ts
│   ├── utils/              # 工具函数
│   │   └── router.tsx
│   ├── styles/             # 全局样式
│   │   └── global.css
│   ├── App.tsx             # 主应用组件
│   └── main.tsx            # 应用入口
├── vite.config.ts          # Vite 配置
└── tsconfig.json           # TypeScript 配置
```

## 🎨 设计特点

- ✅ 深色专业终端风格
- ✅ 等宽字体显示数据
- ✅ 高对比度数据展示
- ✅ 网格背景装饰
- ✅ 响应式布局

## 📝 当前进度

- ✅ 项目结构搭建
- ✅ 路由配置
- ✅ 全局样式和主题配置
- ✅ 首页完整实现
- ⏳ 其他页面占位符（待完善）

## 🔧 技术栈

- React 18 + TypeScript
- Vite
- Ant Design 5.x
- React Router 6
- Axios
- Day.js
