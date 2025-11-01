# 🤖 AI Agent

[![CI/CD Pipeline](https://github.com/mr6923612/AIAgent/workflows/AI%20Agent%20CI/CD%20Pipeline/badge.svg)](https://github.com/mr6923612/AIAgent/actions)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen)](https://github.com/mr6923612/AIAgent/actions)

Intelligent AI agent system based on CrewAI, integrated with RAGFlow knowledge retrieval, supporting one-click local Docker deployment.

## ✨ Core Features

### 🤖 Intelligent Conversation
- Intelligent conversation based on Google AI (Gemini)
- Natural language understanding and generation
- Multi-turn conversation context management

### 📚 Knowledge Retrieval (RAGFlow)
- Integrated RAGFlow for knowledge retrieval
- Vectorized document storage and retrieval
- Precise Q&A support

### 💾 High Availability Session Management
- ✅ **One-to-One Mapping**: Frontend session ↔ RAGFlow session
- ✅ **Auto Recovery**: Restore mappings from database after service restart
- ✅ **Smart Cleanup**: Automatically clean invalid sessions on startup
- ✅ **Database Reconnection**: Auto-recover from network failures
- ✅ **Three-Tier Lookup**: Memory → Database → Create

### 🛠️ Development Features
- 🎨 Modern React frontend interface
- 🐳 Complete Docker containerization
- 🔄 GitHub Actions CI/CD
- 🎛️ YAML-configured Prompts
- 📊 MySQL data persistence

## 📑 Table of Contents

### 📘 Deployment & Configuration
- [🚀 Quick Start](#-quick-start) - Environment requirements, deployment steps
- [🔧 Configuration](#-configuration) - API keys, environment variables
- [🤖 Custom Prompt](#-custom-ai-agent-prompt) - Agent configuration guide
- [🛠️ Troubleshooting](#️-troubleshooting) - Common issues, performance optimization

### 📚 Technical Documentation
- [🌐 Service Architecture](#-service-architecture) - Component relationships, data flow
- [🏗️ Code Architecture](#️-code-architecture) - Core classes, design patterns
- [🆘 Get Help](#-get-help) - Contact information

---

## 🚀 Quick Start

### 📋 Environment Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+
- 4GB+ RAM
- 2GB+ available disk space

---

### 🎯 Deployment Steps

#### Step 1: Clone the Project
```bash
git clone <your-repo-url>
cd AIAgent
```

#### Step 2: Start RAGFlow Service
```bash
cd ragflow/docker
docker-compose up -d
cd ../..
```

Wait approximately 30-60 seconds for RAGFlow to fully start.

#### Step 3: Register RAGFlow and Get API Key
1. Visit http://localhost:80
2. First-time access requires account registration (recommended: `rag@flow.io` / `infiniflow1`)
3. After logging in, go to **Settings** → **API Keys**
4. Click **Create API Key** and copy the generated key

#### Step 4: Create and Configure .env File
```bash
cd crewaiBackend
# Copy template file
cp env.template .env
```

Edit the `.env` file and fill in the following API keys:
```bash
# Google AI API Key (obtain from https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY=your_google_api_key_here

# RAGFlow API Key (obtained from previous step)
RAGFLOW_API_KEY=ragflow-xxxxxxxxxxxxx
```

#### Step 5: Configure Agent Prompt (Optional)
```bash
# Edit agent_config.yaml to customize AI Agent behavior and response style
nano agent_config.yaml
```

#### Step 6: Run Configuration Script
```bash
# Automatically get RAGFlow Chat ID and update configuration
python crewaiBackend/scripts/update_agent_prompt.py --yes
```

> **💡 Note**: This script will automatically:
> - Validate `.env` file configuration
> - Get Chat ID from RAGFlow and update `.env`
> - Update Agent prompt according to `agent_config.yaml`

#### Step 7: Start AI Agent Service
```bash
cd ..  # Return to project root directory
chmod +x quick-start.sh
./quick-start.sh
```

> **Note**: `quick-start.sh` will restart all services, including RAGFlow

#### Step 8: Access Application
- 🌐 **AI Agent Frontend**: http://localhost:3000
- 🔧 **AI Agent Backend**: http://localhost:8012
- 📚 **RAGFlow Admin**: http://localhost:80

---

### 🛠️ Deployment Script Description

| Script | Function | Description |
|--------|----------|-------------|
| `quick-start.sh` | One-click deployment | Start all services and automatically build latest images |
| `stop-all.sh` | Stop services | Stop all running services |

**Script Features**:
- ✅ Automatically update Docker environment configuration in `.env` file
- ✅ Automatically build latest code images
- ✅ Detect API key configuration status
- ✅ Execute health checks and display service status

**Common Commands**:
```bash
./quick-start.sh    # Start all services
./stop-all.sh       # Stop all services
```
---

## 🔧 Configuration

### ⚙️ Environment Configuration File (.env)

The `.env` file contains all service configurations and API keys, **must be configured correctly** for the system to run.

#### 📝 Key Configuration Items

| Configuration Item | Description | How to Obtain |
|-------------------|-------------|---------------|
| `GOOGLE_API_KEY` | Google AI API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `RAGFLOW_API_KEY` | RAGFlow API key | RAGFlow Admin Interface → Settings → API Keys |
| `RAGFLOW_CHAT_ID` | RAGFlow Chat ID | Run `update_agent_prompt.py` to automatically get |
| `RAGFLOW_BASE_URL` | RAGFlow service address | Docker environment: `http://ragflow-server:80` |
| `MYSQL_HOST` | MySQL host address | Docker environment: `aiagent-mysql` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_DATABASE` | Database name | `aiagent` |
| `MYSQL_USER` | Database username | `aiagent` |
| `MYSQL_PASSWORD` | Database password | `aiagent123` |

#### 🔑 API Key Acquisition

**Google AI API Key**:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Log in with Google account
3. Click "Create API Key"
4. Copy the generated API Key

**RAGFlow API Key**:
1. Visit http://localhost:80
2. Log in to RAGFlow account
3. Go to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the generated key

---

## 🌐 Service Architecture

### 📋 Service Overview

| Service | Port | Function | Dependencies |
|---------|------|----------|--------------|
| **aiagent-frontend** | 3000 | React frontend interface | aiagent-backend |
| **aiagent-backend** | 8012 | Flask API service | MySQL, RAGFlow |
| **aiagent-mysql** | 3306 | MySQL database | - |
| **ragflow-server** | 80 | RAGFlow knowledge retrieval | Ollama, MySQL, Redis |
| **ollama** | 11434 | LLM model service | - |

### 🗄️ Database and Storage Services

- **MySQL**: Store chat sessions, message records
- **Redis**: RAGFlow cache service
- **Elasticsearch**: RAGFlow document indexing
- **MinIO**: RAGFlow file storage

### 🔌 API Interfaces

**AI Agent Backend API**:
- `GET /api/health` - Health check
- `POST /api/crew/{session_id}` - Create AI task
- `GET /api/crew/{session_id}` - Get task status

**RAGFlow API**:
- `POST /api/v1/chats/{chat_id}/sessions` - Create session
- `POST /api/v1/chats/{chat_id}/sessions/{session_id}/completions` - Send message

### 📊 Service Dependencies

```
aiagent-frontend → aiagent-backend → aiagent-mysql
                ↓
              ragflow-server → ollama
                ↓
              MySQL + Redis + Elasticsearch + MinIO
```

### 🧹 RAGFlow Session Cleanup

The system automatically cleans invalid RAGFlow sessions on startup:

1. **Database → RAGFlow**: Clear RAGFlow session IDs that don't exist in database
2. **RAGFlow → Database**: Delete RAGFlow sessions without corresponding database records

---

## 📊 Project Structure

```
AIAgent/
├── crewaiBackend/           # Backend service
│   ├── main.py             # Flask application entry
│   ├── crew.py             # CrewAI Agent definition
│   ├── config.py           # Configuration management
│   ├── agent_config.yaml   # Agent configuration file
│   ├── .env                # Environment variables (needs to be created)
│   ├── env.template        # Environment variable template
│   ├── requirements.txt    # Python dependencies
│   ├── utils/              # Utility modules
│   │   ├── database.py     # Database operations
│   │   ├── ragflow_client.py # RAGFlow API client
│   │   ├── sessionManager.py # Session management
│   │   ├── ragflow_session_manager.py # RAGFlow session management
│   │   ├── session_agent_manager.py # Session Agent management
│   │   ├── jobManager.py  # Task management
│   │   ├── myLLM.py       # LLM configuration
│   │   └── speech_to_text.py # Speech to text
│   ├── scripts/            # Script tools
│   │   └── update_agent_prompt.py # Update Agent configuration
│   └── tests/              # Test files
├── crewaiFrontend/         # Frontend service
│   ├── src/               # React source code
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend Docker configuration
├── ragflow/               # RAGFlow service
│   ├── docker/           # RAGFlow Docker configuration
│   └── docker-compose.yml # RAGFlow service configuration
├── data/                  # Data storage directory
│   ├── aiagent/mysql/    # AI Agent database files
│   ├── ragflow/          # RAGFlow data files
│   └── ollama/models/    # Ollama model files
├── docker-compose.yml     # Main Docker Compose configuration
├── quick-start.sh         # One-click startup script
├── stop-all.sh           # Stop all services script
├── Makefile              # Build and test commands
└── README.md             # Project documentation
```

---

## 🏗️ Code Architecture

### Core Classes and Data Structures

#### 1. Session Management Architecture

**RAGFlowSessionManager (Singleton Pattern)**
```python
class RAGFlowSessionManager:
    def __init__(self):
        self.session_mapping = {}  # Memory mapping: app_session_id -> ragflow_session_id
        self.db_manager = DatabaseManager()
        self.ragflow_client = RAGFlowClient()
    
    def get_or_create_session(self, app_session_id: str) -> str:
        # Three-tier lookup: memory -> database -> create new session
        # 1. Check memory mapping
        # 2. Query database
        # 3. Create new RAGFlow session
```

**SessionAgentManager**
```python
class SessionAgentManager:
    def __init__(self):
        self.session_agents = {}  # session_id -> SessionAgent
    
    def get_or_create_agent(self, session_id: str) -> SessionAgent:
        # Get or create session Agent
        # Pass ragflow_session_id to CrewAI
```

#### 2. Database Architecture

**DatabaseManager**
```python
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _check_connection(self):
        # Auto-reconnect mechanism
        # Auto-recover connection after network failure
```

**Database Table Structure**
```sql
-- Chat session table
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    ragflow_session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Chat message table
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    message TEXT,
    is_user BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

#### 3. CrewAI Integration Architecture

**CrewtestprojectCrew**
```python
class CrewtestprojectCrew:
    def __init__(self):
        self.ragflow_client = RAGFlowClient()
        self.session_manager = SessionManager()
    
    def create_tasks(self, inputs: dict) -> List[Task]:
        # Prefer to use passed ragflow_session_id
        # If not available, query database
        ragflow_session_id = inputs.get('ragflow_session_id')
        if not ragflow_session_id:
            ragflow_session_id = self.session_manager.get_ragflow_session_id(inputs['session_id'])
        
        # Create RAGFlow task
        return [Task(description=..., inputs={'ragflow_session_id': ragflow_session_id})]
```

### Data Flow

#### 1. User Message Processing Flow

```
User sends message
    ↓
Frontend → aiagent-backend API
    ↓
SessionAgentManager.get_or_create_agent()
    ↓
RAGFlowSessionManager.get_or_create_session()
    ↓
CrewAI Agent executes task
    ↓
Call RAGFlow API
    ↓
Return AI reply
    ↓
Frontend displays reply
```

#### 2. Session Recovery Flow

```
Service restart
    ↓
RAGFlowSessionManager initialization
    ↓
_cleanup_invalid_sessions()
    ↓
Database → RAGFlow cleanup
    ↓
RAGFlow → Database cleanup
    ↓
Load valid sessions to memory
    ↓
Service ready
```

#### 3. Three-Tier Lookup Mechanism

```
get_or_create_session(app_session_id)
    ↓
1. Check memory mapping session_mapping[app_session_id]
    ↓ (if found)
    Return ragflow_session_id
    ↓ (if not found)
2. Query database SELECT ragflow_session_id FROM chat_sessions WHERE id = app_session_id
    ↓ (if found)
    Load to memory mapping, return ragflow_session_id
    ↓ (if not found)
3. Create new RAGFlow session
    ↓
    Save to database and memory mapping
    ↓
    Return new ragflow_session_id
```

### Architecture Layers

#### 1. Presentation Layer
- **React Frontend**: User interface and interactions
- **Flask API**: RESTful API interfaces

#### 2. Business Logic Layer
- **SessionAgentManager**: Session Agent management
- **RAGFlowSessionManager**: RAGFlow session management
- **CrewAI Agents**: AI task execution

#### 3. Data Access Layer
- **DatabaseManager**: MySQL database operations
- **RAGFlowClient**: RAGFlow API client
- **SessionManager**: Session data management

#### 4. Infrastructure Layer
- **Docker Containers**: Service containerization
- **MySQL**: Data persistence
- **RAGFlow**: Knowledge retrieval service
- **Ollama**: LLM model service

### Module Responsibilities

#### 1. Core Modules
- **main.py**: Flask application entry, API routes
- **crew.py**: CrewAI Agent definition and task creation
- **config.py**: Configuration management and environment variable loading

#### 2. Utility Modules
- **database.py**: Database connection and operations
- **ragflow_client.py**: RAGFlow API interactions
- **sessionManager.py**: Session data management
- **ragflow_session_manager.py**: RAGFlow session mapping management
- **session_agent_manager.py**: Session Agent lifecycle management
- **jobManager.py**: Async task management
- **myLLM.py**: LLM configuration and calling
- **speech_to_text.py**: Speech to text functionality

#### 3. Configuration Modules
- **agent_config.yaml**: Agent behavior configuration
- **.env**: Environment variable configuration
- **docker-compose.yml**: Service orchestration configuration

### Design Principles

#### 1. Single Responsibility Principle
- Each module only responsible for one specific function
- Database operations, API calls, session management separated

#### 2. Dependency Injection
- Inject dependencies through constructors
- Easy to test and replace modules

#### 3. Error Handling
- Unified exception handling mechanism
- Auto-retry and recovery mechanisms

#### 4. Configuration-Driven
- Control behavior through configuration files
- Support environment variable overrides

### Core Optimizations

#### 1. Session Management Optimization
```python
# Singleton pattern ensures unique instance
class RAGFlowSessionManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### 2. Three-Tier Lookup Mechanism
```python
def get_or_create_session(self, app_session_id: str) -> str:
    # 1. Memory lookup
    if app_session_id in self.session_mapping:
        return self.session_mapping[app_session_id]
    
    # 2. Database lookup
    ragflow_session_id = self.db_manager.get_ragflow_session_id(app_session_id)
    if ragflow_session_id:
        self.session_mapping[app_session_id] = ragflow_session_id
        return ragflow_session_id
    
    # 3. Create new session
    return self._create_new_session(app_session_id)
```

#### 3. Bidirectional Cleanup Mechanism
```python
def _cleanup_invalid_sessions(self):
    # Database → RAGFlow cleanup
    self._cleanup_database_to_ragflow()
    
    # RAGFlow → Database cleanup
    self._cleanup_ragflow_to_database()
```

#### 4. Auto-Reconnect Mechanism
```python
def _check_connection(self):
    try:
        self.connection.ping(reconnect=True)
    except Exception:
        self._connect()  # Auto-reconnect
```

#### 5. Object Reuse Optimization
```python
class SessionAgent:
    def __init__(self):
        self._crew_helper = CrewtestprojectCrew()  # Create once, reuse
    
    def _create_agents(self):
        return self._crew_helper.create_agents()
    
    def _create_crew(self):
        return self._crew_helper.create_crew()
```

**Effect**: ✅ Reduce resource consumption, improve performance

---

## 🧪 Testing & CI/CD

### Run Tests
```bash
# Run all tests
make test

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

### CI/CD Process
- **GitHub Actions**: Auto testing, building, deployment
- **Status**: [View Pipeline](https://github.com/mr6923612/AIAgent/actions)
- **Local Development**: `make dev` → `make test` → `make deploy`

## 📁 Data Management

The project uses a unified data folder structure:

```
data/
├── aiagent/mysql/     # AI Agent database
├── ragflow/          # RAGFlow service data
└── ollama/models/    # Ollama model files
```

**Advantages**: Data isolation, easy backup, support Docker volume mounting

## 🛠️ Troubleshooting

### Port Conflicts
If encountering port conflicts, modify port mappings in `docker-compose.yml`:

```yaml
services:
  aiagent-frontend:
    ports:
      - "3001:3000"  # Change to port 3001
```

### Services Unreachable
1. Check if services are running:
   ```bash
   docker-compose --profile aiagent ps
   ```

2. View service logs:
   ```bash
   docker-compose --profile aiagent logs aiagent-backend
   ```

### Database Connection Issues
```bash
# Check MySQL service status
docker-compose --profile aiagent logs aiagent-mysql

# Restart database service
docker-compose --profile aiagent restart aiagent-mysql
```

### Common Issue Solutions

#### 1. Docker Build Failure
**Issue**: `failed to prepare extraction snapshot: parent snapshot does not exist`

**Solution**:
```bash
# Clean Docker build cache
docker builder prune -af
docker image prune -af

# Rebuild (without cache)
docker-compose --profile aiagent up -d --build --no-cache
```

#### 2. RAGFlow API Authentication Failed
**Issue**: `RAGFlow API error: Authentication error: API key is invalid!`

**Solution**:
1. Visit http://localhost:80
2. Go to **Settings** → **API Keys**
3. Create new API Key
4. Update `RAGFLOW_API_KEY` in `crewaiBackend/.env` file

#### 3. Session Management Issues
**Issue**: New RAGFlow session created on every request

**Solution**:
1. Check if database connection is normal
2. Ensure `ragflow_session_manager` is properly initialized
3. View backend logs to confirm session mapping is normal

#### 4. Service Startup Order Issues
**Solution**:
1. Start RAGFlow first: `cd ragflow/docker && docker-compose up -d`
2. Wait 30-60 seconds for RAGFlow to fully start
3. Then start AI Agent: `./quick-start.sh`

### Performance Optimization Recommendations

1. **Resource Requirements**: At least 4GB RAM, 2GB available disk space
2. **Port Management**: Ensure ports 3000-12000 are available
3. **Network Isolation**: All services communicate in `aiagent-net` network
4. **Firewall**: Allow necessary port access

### Ollama and RAGFlow Configuration

#### 1. Ollama Model Management
The system automatically downloads the **bge-m3** model for text embedding.

```bash
# View installed models
docker exec ollama ollama list

# Manually download model (if needed)
docker exec ollama ollama pull bge-m3
```

#### 2. RAGFlow Configure Ollama
Visit http://localhost:80, go to **Settings** → **Model Management**:

| Configuration Item | Value | Description |
|-------------------|-------|-------------|
| API Address | `http://ollama:11434` | ⚠️ Must use container name instead of localhost |
| Model Name | `bge-m3:latest` | Embedding model |

**Verify Connection**:
```bash
docker exec ragflow-server curl http://ollama:11434
```

**Common Issues**:
- **Connection Failed**: Ensure using `http://ollama:11434` instead of `localhost`
- **Model Not Found**: Run `docker exec ollama ollama pull bge-m3`

## 🤖 Custom AI Agent Prompt

### Quick Configuration

1. **Edit Configuration**: Modify `crewaiBackend/agent_config.yaml`
2. **Apply Configuration**: Run `python crewaiBackend/scripts/update_agent_prompt.py --yes`
3. **Restart Service**: `docker-compose --profile aiagent restart aiagent-backend`

### Configuration Items

| Configuration Item | Description | Example |
|-------------------|-------------|---------|
| `agent_name` | Agent name | "Intelligent Customer Service" |
| `role` | Agent role | "Professional customer service representative" |
| `goal` | Agent goal | "Provide accurate and friendly customer service" |
| `backstory` | Agent background | "I am an experienced customer service expert..." |
| `verbose` | Detailed logging | `true` / `false` |
| `max_iter` | Maximum iterations | `3` |
| `max_execution_time` | Maximum execution time (seconds) | `300` |

### Troubleshooting

**Issue**: "API key is invalid"
- **Solution**: Ensure `RAGFLOW_API_KEY` in `.env` file is correct

**Issue**: "You do not own the assistant"
- **Solution**: Re-run configuration script to get correct `CHAT_ID`

**Issue**: "Connection refused"
- **Solution**: Ensure RAGFlow service is running

## 🆘 Get Help

- **GitHub Issues**: [Submit Issue](https://github.com/mr6923612/AIAgent/issues)
- **Documentation**: View project documentation and configuration instructions
- **Community**: Participate in discussions and contribute code

---

**🎉 Thank you for using AI Agent!**
