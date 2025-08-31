import asyncio, json, subprocess, uuid
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import get_db, create_tables
import models
import schemas

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(title="Computer Use Agent Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Enhanced websocket connection manager with session support ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # session_id -> [websockets]

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.active_connections[session_id].remove(connection)

manager = ConnectionManager()

# ---- Database Operations ----
def create_session(db: Session, session_id: str):
    db_session = models.Session(session_id=session_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str):
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def add_message(db: Session, session_id: str, content: str, message_type: str):
    session = get_session(db, session_id)
    if session:
        message = models.Message(
            session_id=session.id,
            content=content,
            message_type=message_type
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    return None

def add_tool_run(db: Session, session_id: str, tool_name: str, command: str, status: str = "running"):
    session = get_session(db, session_id)
    if session:
        tool_run = models.ToolRun(
            session_id=session.id,
            tool_name=tool_name,
            command=command,
            status=status
        )
        db.add(tool_run)
        db.commit()
        db.refresh(tool_run)
        return tool_run
    return None

def update_tool_run(db: Session, tool_run_id: int, status: str, output: str = None, error: str = None):
    tool_run = db.query(models.ToolRun).filter(models.ToolRun.id == tool_run_id).first()
    if tool_run:
        tool_run.status = status
        tool_run.output = output
        tool_run.error = error
        if status in ["completed", "failed"]:
            tool_run.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(tool_run)
        return tool_run
    return None

# ---- API Routes ----
@app.get("/", response_class=HTMLResponse)
async def index():
    return open("static/index.html", "r", encoding="utf-8").read()

@app.post("/api/sessions", response_model=schemas.SessionResponse)
async def create_new_session(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = create_session(db, session_id)
    return session

@app.get("/api/sessions/{session_id}", response_model=schemas.SessionWithData)
async def get_session_data(session_id: str, db: Session = Depends(get_db)):
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(models.Message).filter(models.Message.session_id == session.id).all()
    tool_runs = db.query(models.ToolRun).filter(models.ToolRun.session_id == session.id).all()
    
    return schemas.SessionWithData(
        session=session,
        messages=messages,
        tool_runs=tool_runs
    )

@app.get("/api/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.Session).filter(models.Session.is_active == True).all()
    return sessions

# ---- Enhanced Command Execution with Session Management ----
async def execute_command(command: str, session_id: str, db: Session):
    try:
        # Add user message to database
        add_message(db, session_id, command, "user")
        
        # Create tool run record
        tool_run = add_tool_run(db, session_id, "computer_control", command)
        
        # Send progress updates
        await manager.send_to_session(session_id, {
            "type": "progress", 
            "step": 1, 
            "text": "Initializing computer use tools...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        await manager.send_to_session(session_id, {
            "type": "progress", 
            "step": 2, 
            "text": "Analyzing command...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        # Execute based on command type
        command_lower = command.lower()
        result = None
        
        if "browser" in command_lower or "firefox" in command_lower:
            await manager.send_to_session(session_id, {
                "type": "progress", 
                "step": 3, 
                "text": "Opening Firefox browser...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && firefox-esr &"
            ], capture_output=True, text=True)
            
        elif "screenshot" in command_lower or "screen" in command_lower:
            await manager.send_to_session(session_id, {
                "type": "progress", 
                "step": 3, 
                "text": "Taking screenshot...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && gnome-screenshot -f /tmp/screenshot.png -p"
            ], capture_output=True, text=True)
            
        elif "terminal" in command_lower or "xterm" in command_lower:
            await manager.send_to_session(session_id, {
                "type": "progress", 
                "step": 3, 
                "text": "Opening terminal...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && xterm &"
            ], capture_output=True, text=True)
            
        elif "click" in command_lower or "mouse" in command_lower:
            await manager.send_to_session(session_id, {
                "type": "progress", 
                "step": 3, 
                "text": "Executing mouse action...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            if "left" in command_lower:
                result = subprocess.run([
                    "docker", "exec", "computer-use-demo", 
                    "bash", "-c", "export DISPLAY=:1 && xdotool click 1"
                ], capture_output=True, text=True)
            elif "right" in command_lower:
                result = subprocess.run([
                    "docker", "exec", "computer-use-demo", 
                    "bash", "-c", "export DISPLAY=:1 && xdotool click 3"
                ], capture_output=True, text=True)
            else:
                result = subprocess.run([
                    "docker", "exec", "computer-use-demo", 
                    "bash", "-c", "export DISPLAY=:1 && xdotool click 1"
                ], capture_output=True, text=True)
                
        else:
            await manager.send_to_session(session_id, {
                "type": "progress", 
                "step": 3, 
                "text": "Executing custom command...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", f"export DISPLAY=:1 && {command}"
            ], capture_output=True, text=True)
        
        await manager.send_to_session(session_id, {
            "type": "progress", 
            "step": 4, 
            "text": "Processing result...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        # Update tool run with result
        if result and hasattr(result, 'returncode'):
            if result.returncode == 0:
                output = result.stdout or "Command executed successfully"
                status = "completed"
                error = None
                message_text = f"Completed: {command}\nOutput: {output}"
                message_type = "assistant"
            else:
                error = result.stderr or "Command failed"
                status = "failed"
                output = None
                message_text = f"Command failed: {command}\nError: {error}"
                message_type = "system"
        else:
            status = "completed"
            output = "Command executed"
            error = None
            message_text = f"Completed: {command}"
            message_type = "assistant"
        
        # Update tool run
        update_tool_run(db, tool_run.id, status, output, error)
        
        # Add response message to database
        add_message(db, session_id, message_text, message_type)
        
        # Send completion message
        await manager.send_to_session(session_id, {
            "type": "final", 
            "text": message_text, 
            "ts": datetime.utcnow().isoformat()
        })
            
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        
        # Update tool run with error
        if tool_run:
            update_tool_run(db, tool_run.id, "failed", None, error_msg)
        
        # Add error message to database
        add_message(db, session_id, error_msg, "system")
        
        # Send error message
        await manager.send_to_session(session_id, {
            "type": "error", 
            "text": error_msg, 
            "ts": datetime.utcnow().isoformat()
        })
        print(f"Error in execute_command: {e}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            
            if data.get("type") == "command":
                command = data.get("content", "")
                # Get database session and execute command
                db = next(get_db())
                asyncio.create_task(execute_command(command, session_id, db))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
