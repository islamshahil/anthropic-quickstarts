# Computer Use Agent - FastAPI Backend

## New Built

Successfully transformed the experimental Streamlit-based computer use demo into a **scalable FastAPI backend**

## Architecture Comparison: Original vs New System

### **Original System (Single Container):**
- **1 Dockerfile** → builds `computer-use-demo:local` image
- **1 Container** → runs everything (VNC + Streamlit + AI Agent)

### **New System (Multi-Container):**
- **1 docker-compose.yml** → orchestrates 2 containers
- **2 Containers:**
  - `computer-use-demo` → VNC Desktop + AI Agent (original functionality)
  - `fastapi-backend` → New REST API + Web Interface

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
│  │ • Original     │    │ • Port 8000                     │ │
│  │   functionality│    │                                 │ │
│  │ • Ports:       │    │                                 │ │
│  │   5900,6080,   │    │                                 │ │
│  │   8080,8501    │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```


## 📁 Project Structure

```
computer-use-demo/
├── docker-compose.yml          # Main orchestration
├── fastapi_backend/            # FastAPI application
│   ├── main.py                # Main FastAPI app
│   ├── requirements.txt       # Python dependencies
│   └── static/                # Frontend files
│       └── index.html         # Web interface
└── README_FASTAPI.md          # This file
```


## How to Run the NEW FastAPI System

### 1. **Start the System**
```bash
docker-compose up -d
```

### 2. **Access the Interface**
- **FastAPI Frontend**: http://localhost:8000/
- **VNC Desktop**: http://localhost:6080/

### 3. **Try Commands**
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

