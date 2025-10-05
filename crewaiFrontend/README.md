# CrewAI Chat - React 前端应用

这是一个基于React的智能聊天界面，集成了CrewAI后端服务，提供类似ChatGPT的用户体验。

## 功能特性

- 🔐 **用户认证系统** - 完整的登录和注册功能，支持用户名密码登录
- 💬 **智能聊天界面** - 类似ChatGPT的对话界面，支持实时消息
- 🤖 **CrewAI集成** - 与后端CrewAI服务无缝集成，提供智能项目分析
- 📱 **响应式设计** - 支持桌面和移动设备
- 🎨 **现代化UI** - 美观的渐变色彩和流畅的动画效果

## 技术栈

- **React 18** - 前端框架
- **React Router** - 路由管理
- **Vite** - 构建工具
- **Axios** - HTTP客户端
- **Lucide React** - 图标库
- **CSS3** - 样式设计

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── components/
│   ├── Login.jsx          # 登录组件
│   ├── Login.css          # 登录样式
│   ├── Register.jsx       # 注册组件
│   ├── Register.css       # 注册样式
│   ├── ChatInterface.jsx  # 聊天界面组件
│   └── ChatInterface.css  # 聊天界面样式
├── App.jsx                # 主应用组件
├── App.css                # 应用样式
├── main.jsx               # 应用入口
└── index.css              # 全局样式
```

## 使用说明

### 登录和注册
- **注册**：在注册页面填写用户名、邮箱和密码创建新账户
- **登录**：在登录页面输入用户名和密码即可登录
- 登录状态会保存在本地存储中
- 支持在登录和注册页面之间切换

### 聊天功能
- 在聊天界面输入您的项目需求描述
- 系统会自动调用CrewAI后端服务进行分析
- 支持实时查看处理进度和结果

### 后端集成
- 默认连接到 http://127.0.0.1:8012
- 确保CrewAI后端服务正在运行
- 支持项目描述和域名分析功能

## 开发说明

### 添加新功能
1. 在 `src/components/` 目录下创建新组件
2. 在 `App.jsx` 中导入并使用组件
3. 添加相应的CSS样式文件

### 修改API端点
在 `ChatInterface.jsx` 中修改API URL：
```javascript
const response = await axios.post('http://127.0.0.1:8012/api/crew', {
  // API调用
});
```

### 自定义样式
- 全局样式：`src/index.css`
- 组件样式：各组件对应的CSS文件
- 使用CSS变量可以轻松修改主题色彩

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 许可证

MIT License