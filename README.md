# CrewAI 全栈智能应用

本项目是一个完整的AI应用全栈项目，使用 **Flask + React + CrewAI** 构建，提供类似ChatGPT的智能对话体验。

## 🚀 项目特性

- **智能对话界面** - 基于React的现代化聊天界面，类似ChatGPT的用户体验
- **用户认证系统** - 完整的登录/登出功能
- **多Agent协作** - 基于CrewAI的智能营销分析系统
- **实时处理** - 支持异步任务处理和实时状态更新
- **响应式设计** - 支持桌面和移动设备

## 📁 项目结构

```
CrewAIFullstackTest/
├── crewaiBackend/          # Flask后端服务
│   ├── main.py            # 主服务文件
│   ├── crew.py            # CrewAI配置
│   └── utils/             # 工具模块
├── crewaiFrontend/         # React前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── App.jsx        # 主应用
│   │   └── main.jsx       # 入口文件
│   └── package.json       # 依赖配置
└── README.md              # 项目说明
```

## 🛠️ 技术栈

### 后端
- **Flask** - Python Web框架
- **CrewAI** - 多Agent协作框架
- **Flask-CORS** - 跨域支持

### 前端
- **React 18** - 前端框架
- **React Router** - 路由管理
- **Vite** - 构建工具
- **Axios** - HTTP客户端
- **Lucide React** - 图标库

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd crewaiBackend
pip install -r requirements.txt
python main.py
```

后端服务将在 http://127.0.0.1:8012 启动

### 2. 启动前端应用

```bash
cd crewaiFrontend
npm install
npm run dev
```

前端应用将在 http://localhost:3000 启动

### 3. 使用应用

1. 打开浏览器访问 http://localhost:3000
2. 使用任意用户名和密码登录
3. 在聊天界面输入您的项目需求
4. 系统将调用CrewAI进行智能分析

## 📖 使用说明

### 登录功能
- 支持任意用户名和密码登录（演示用途）
- 登录状态会保存在本地存储中
- 支持登出功能

### 聊天功能
- 输入项目描述，系统会自动分析
- 支持实时查看处理进度
- 自动提取域名信息进行分析

### 后端API
- `POST /api/crew` - 启动CrewAI分析任务
- `GET /api/crew/<job_id>` - 查询任务状态

## 🎯 项目亮点

本项目将原有的Vue.js前端升级为React，并添加了完整的用户认证和聊天界面功能，提供了更好的用户体验。             

**定义了3个Agent**        
**lead_market_analyst:**                      
  role: >            
    首席市场分析师               
  goal: >              
    以敏锐的洞察力对客户提供的产品和竞争对手进行深入的剖析，并为营销战略的制定提供专业指导。              
  backstory: >               
    你任职在一家一流数字营销公司，你的职位是首席市场分析师。               
    你的专长是以敏锐的洞察力对客户提供的产品和竞争对手进行深入的剖析。                     
**chief_marketing_strategist:**                            
  role: >               
    首席营销战略师                 
  goal: >               
    基于产品的市场分析内容，以敏锐的洞察力制定出令人惊喜的营销战略。                   
  backstory: >                 
    你任职在一家一流数字营销公司，你的职位是首席营销战略师。                  
    你的专长是能够制定出成功的定制营销战略。               
**creative_content_creator:**                     
  role: >               
    首席创意内容创作师               
  goal: >                  
    基于产品的营销战略内容，为社交媒体活动开发有吸引力的创新内容。               
    重点是创建高影响力的广告文案。                 
  backstory: >               
    你任职在一家一流数字营销公司，你的职位是首席创意内容创作师。             
    你的专长是能够将营销战略转化为引人入胜的故事和视觉内容，吸引注意力并激发行动。               
**定义了5个Task**                   
**research_task:**             
  description: >                
    基于客户提供的{customer_domain}对客户提供的产品和竞争对手进行深入的剖析。请确保找到任何有趣的相关信息，日期限定为2024年。                
    我们正在就以下项目与他们合作：            
    {project_description}。            
  expected_output: >              
    关于客户、客户提供的产品和竞争对手的完整报告、包括指标统计、偏好、市场定位和受众参与度。              
  agent: lead_market_analyst                      
**project_understanding_task:**                 
  description: >                    
    了解{project_description}的项目细节和目标受众。查看提供的任何材料，并根据需要收集更多信息。                 
  expected_output: >                  
    项目的详细摘要和目标受众的简介。                 
  agent: chief_marketing_strategist                   
**marketing_strategy_task:**               
  description: >                 
    基于客户提供的{customer_domain}和{project_description}为项目制定全面的营销战略。                   
    充分使用从研究任务和项目理解任务中获得的见解来制定高质量的战略。               
  expected_output: >                  
    一份详细的营销战略文件，概述目标、目标受众、关键信息和建议的策略，确保包含名称、策略、渠道和关键绩效指标。                   
  agent: chief_marketing_strategist                
**campaign_idea_task:**                  
  description: >                  
    为{project_description}开发富有创意的营销活动构思。               
    确保创意新颖、吸引人，并与整体营销战略保持一致。                 
  expected_output: >                  
    列出 5 个活动设想，每个设想都有简要说明和预期影响。                   
  agent: creative_content_creator                      
**copy_creation_task:**                
  description: >                  
    根据已获批准的{project_description}活动创意制作营销文案。                   
    确保文案引人注目、清晰明了，并适合目标受众。                  
  expected_output: >                 
    每个活动创意的营销副本。                  
  agent: creative_content_creator                                                                     
