import asyncio, json, subprocess
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Computer Use Agent Backend")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Simple websocket connection manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_to_all(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# ---- Routes ----
@app.get("/", response_class=HTMLResponse)
async def index():
    return open("static/index.html", "r", encoding="utf-8").read()

# Real command execution using direct system calls
async def execute_command(command: str):
    try:
        await manager.send_to_all({
            "type": "progress", 
            "step": 1, 
            "text": "Initializing computer use tools...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        await manager.send_to_all({
            "type": "progress", 
            "step": 2, 
            "text": "Analyzing command...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        # Execute based on command type
        command_lower = command.lower()
        result = None
        
        if "browser" in command_lower or "firefox" in command_lower:
            await manager.send_to_all({
                "type": "progress", 
                "step": 3, 
                "text": "Opening Firefox browser...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            # Use docker exec to run command in the computer-use-demo container
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && firefox-esr &"
            ], capture_output=True, text=True)
            
        elif "screenshot" in command_lower or "screen" in command_lower:
            await manager.send_to_all({
                "type": "progress", 
                "step": 3, 
                "text": "Taking screenshot...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            # Use docker exec to take screenshot in the computer-use-demo container
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && gnome-screenshot -f /tmp/screenshot.png -p"
            ], capture_output=True, text=True)
            
        elif "terminal" in command_lower or "xterm" in command_lower:
            await manager.send_to_all({
                "type": "progress", 
                "step": 3, 
                "text": "Opening terminal...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            # Use docker exec to open terminal in the computer-use-demo container
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", "export DISPLAY=:1 && xterm &"
            ], capture_output=True, text=True)
            
        elif "click" in command_lower or "mouse" in command_lower:
            await manager.send_to_all({
                "type": "progress", 
                "step": 3, 
                "text": "Executing mouse action...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            # Use docker exec to perform mouse click in the computer-use-demo container
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
            await manager.send_to_all({
                "type": "progress", 
                "step": 3, 
                "text": "Executing custom command...", 
                "ts": datetime.utcnow().isoformat()
            })
            
            # Use docker exec for custom commands in the computer-use-demo container
            result = subprocess.run([
                "docker", "exec", "computer-use-demo", 
                "bash", "-c", f"export DISPLAY=:1 && {command}"
            ], capture_output=True, text=True)
        
        await manager.send_to_all({
            "type": "progress", 
            "step": 4, 
            "text": "Processing result...", 
            "ts": datetime.utcnow().isoformat()
        })
        
        # Send completion with actual result
        if result and hasattr(result, 'returncode'):
            if result.returncode == 0:
                output = result.stdout or "Command executed successfully"
                await manager.send_to_all({
                    "type": "final", 
                    "text": f"Completed: {command}\nOutput: {output}", 
                    "ts": datetime.utcnow().isoformat()
                })
            else:
                error = result.stderr or "Command failed"
                await manager.send_to_all({
                    "type": "error", 
                    "text": f"Command failed: {command}\nError: {error}", 
                    "ts": datetime.utcnow().isoformat()
                })
        else:
            await manager.send_to_all({
                "type": "final", 
                "text": f"Completed: {command}", 
                "ts": datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        # Send error message
        await manager.send_to_all({
            "type": "error", 
            "text": f"Error executing command: {str(e)}", 
            "ts": datetime.utcnow().isoformat()
        })
        print(f"Error in execute_command: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            
            if data.get("type") == "command":
                # Execute the command directly
                command = data.get("content", "")
                asyncio.create_task(execute_command(command))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
