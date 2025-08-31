# Computer Use Agent - FastAPI Backend

## New Built

Successfully transformed the experimental Streamlit-based computer use demo into a **scalable FastAPI backend**

## Architecture Comparison: Original vs New System

### **Original System (Single Container):**
- **1 Dockerfile** → builds `computer-use-demo:local` image
- **1 Container** → runs everything (VNC + Streamlit + AI Agent)

### **New System (Multi-Container):**
- **1 docker-compose.yml** → orchestrates 3 containers
- **3 Containers:**
  - `computer-use-demo` → VNC Desktop + AI Agent (original functionality)
  - `fastapi-backend` → New REST API + Web Interface + Session Management
  - `computer-use-postgres` → PostgreSQL Database for persistent storage

## New System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    docker-compose.yml                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ computer-use-   │    │        fastapi-backend          │ │
│  │ demo            │    │                                 │ │
│  │                 │    │ • FastAPI REST API              │ │
│  │ • VNC Desktop  │    │ • WebSocket for real-time       │ │
│  │ • AI Agent     │    │ • HTML/JS Frontend              │ │
│  │ • Streamlit    │    │ • Docker CLI for VNC control    │ │
│  │ • Original     │    │ • Session Management            │ │
│  │   functionality│    │ • Database Integration          │ │
│  │ • Ports:       │    │ • Port 8000                     │ │
│  │   5900,6080,   │    │                                 │ │
│  │   8080,8501    │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              computer-use-postgres                     │ │
│  │                                                         │ │
│  │ • PostgreSQL Database                                  │ │
│  │ • Persistent Session Storage                           │ │
│  │ • Chat History & Command Logs                         │ │
│  │ • Port 5432                                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```


## Project Structure

```
computer-use-demo/
├── docker-compose.yml          # Main orchestration (3 services)
├── fastapi_backend/            # FastAPI application
│   ├── main.py                # Main FastAPI app with session management
│   ├── models.py              # SQLAlchemy database models
│   ├── database.py            # Database connection & setup
│   ├── schemas.py             # Pydantic data validation schemas
│   ├── requirements.txt       # Python dependencies
│   └── static/                # Frontend files
│       └── index.html         # Enhanced web interface
└── README_FASTAPI.md          # This file
```


### 1. **Start the Complete System**
```bash
cd computer-use-demo
docker-compose up -d
```

### 2. **Verify All Services**
```bash
docker-compose ps
```
You should see:
- ✅ `computer-use-demo` - VNC Desktop + AI Agent
- ✅ `computer-use-postgres` - PostgreSQL Database
- ✅ `fastapi-backend` - FastAPI + Session Management

### 3. **Access the Enhanced Interface**
- **FastAPI Frontend**: http://localhost:8000/
- **VNC Desktop**: http://localhost:6080/
- **Database**: localhost:5432 (if needed for debugging)

### 4. **Start Using Enhanced Features**

#### **Create a New Session:**
1. Click **"🆕 New Session"** button
2. System generates unique session ID
3. WebSocket connects automatically
4. Chat interface becomes active

#### **Execute Commands:**
Type these in the chat interface:
- `"open browser"` → Opens Firefox in VNC
- `"take screenshot"` → Takes real screenshot
- `"open terminal"` → Opens xterm in VNC
- `"click mouse"` → Performs real mouse click

## How to Run the OLD System (Streamlit)


### 1. **Run the original system**
```bash
docker run -d \
  --name computer-use-demo \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -p 5900:5900 \
  -p 8501:8501 \
  -p 6080:6080 \
  ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
```

### 2. **Access Streamlit interface**
- **Streamlit**: http://localhost:8501/
- **VNC**: http://localhost:6080/

