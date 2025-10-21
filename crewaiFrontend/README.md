# CrewAI Frontend

基于React的智能客服前端界面，支持多模态输入和实时对话。

## 🚀 功能特性

- **实时对话**: 与AI客服进行实时对话
- **多模态输入**: 支持文本、图片、语音输入
- **多语言支持**: 自动识别语言并提供相应回复
- **用户认证**: 完整的注册和登录系统
- **超时处理**: 1分钟超时机制
- **响应式设计**: 适配各种屏幕尺寸

## 📁 目录结构

```
crewaiFrontend/
├── src/
│   ├── components/        # React组件
│   │   ├── ChatInterface.jsx    # 聊天界面
│   │   ├── Login.jsx            # 登录组件
│   │   └── Register.jsx         # 注册组件
│   ├── App.jsx            # 主应用组件
│   └── main.jsx           # 应用入口
├── public/                # 静态资源
├── package.json           # 项目配置
└── vite.config.js         # Vite配置
```

## 🛠️ 技术栈

- **React 18**: 前端框架
- **Vite**: 构建工具
- **Axios**: HTTP客户端
- **Lucide React**: 图标库

## 🚀 快速开始

### 环境要求
- Node.js 16+
- npm 或 yarn

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 构建生产版本
```bash
npm run build
```

## 🎨 界面特性

### 聊天界面
- **消息气泡**: 用户和AI消息分别显示
- **加载动画**: 显示AI思考状态
- **文件预览**: 上传文件的预览功能
- **滚动自动**: 自动滚动到最新消息

### 输入功能
- **文本输入**: 支持多行文本输入
- **图片上传**: 支持拖拽和点击上传
- **语音录制**: 支持语音录制和发送
- **快捷键**: Enter发送，Shift+Enter换行

### 用户界面
- **登录/注册**: 完整的用户认证流程
- **用户信息**: 显示当前登录用户
- **退出功能**: 安全的登出操作

## 🔧 核心组件

### ChatInterface (`src/components/ChatInterface.jsx`)

主要的聊天界面组件，包含：
- 消息显示和管理
- 多模态输入处理
- 实时状态更新
- 超时处理机制

#### 主要功能

```javascript
// 发送消息
const handleSubmit = async (e) => {
  // 处理文本、图片、语音输入
  // 发送到后端API
  // 管理加载状态
};

// 检查任务状态
useEffect(() => {
  // 轮询检查任务状态
  // 处理完成和错误状态
  // 超时处理
}, [currentJobId, isLoading]);
```

### Login/Register (`src/components/Login.jsx`, `src/components/Register.jsx`)

用户认证组件：
- 表单验证
- API调用
- 错误处理
- 状态管理

## 📱 响应式设计

### 断点设置
- **移动端**: < 768px
- **平板端**: 768px - 1024px
- **桌面端**: > 1024px

### 适配特性
- 弹性布局
- 自适应字体大小
- 触摸友好的按钮
- 移动端优化的输入框

## 🔌 API集成

### 后端通信
```javascript
// 发送消息
const response = await axios.post('/api/crew', {
  customer_input: inputValue,
  input_type: 'text',
  // ...其他参数
});

// 检查任务状态
const statusResponse = await axios.get(`/api/crew/${jobId}`);
```

### 错误处理
- 网络错误处理
- 超时处理
- 用户友好的错误提示

## ⚡ 性能优化

### 代码分割
- 路由级别的代码分割
- 组件懒加载
- 动态导入

### 状态管理
- React Hooks
- 本地状态管理
- 避免不必要的重渲染

### 资源优化
- 图片压缩
- 代码压缩
- 缓存策略

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
npm test

# 运行特定测试
npm test ChatInterface
```

### 测试覆盖
- 组件渲染测试
- 用户交互测试
- API调用测试
- 错误处理测试

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   - 检查后端服务状态
   - 验证API地址配置
   - 检查网络连接

2. **文件上传失败**
   - 检查文件大小限制
   - 验证文件格式
   - 检查浏览器权限

3. **语音录制失败**
   - 检查麦克风权限
   - 验证浏览器支持
   - 检查HTTPS要求

## 📝 开发指南

### 添加新功能

1. **新组件**: 在`src/components/`中创建
2. **新页面**: 在`src/`中创建页面组件
3. **新样式**: 使用CSS模块或内联样式

### 代码规范

- 使用函数组件和Hooks
- 添加PropTypes或TypeScript
- 遵循ESLint规则
- 编写组件文档

### 状态管理

```javascript
// 使用useState管理本地状态
const [messages, setMessages] = useState([]);
const [isLoading, setIsLoading] = useState(false);

// 使用useEffect处理副作用
useEffect(() => {
  // 副作用逻辑
}, [dependencies]);
```

## 📄 许可证

MIT License