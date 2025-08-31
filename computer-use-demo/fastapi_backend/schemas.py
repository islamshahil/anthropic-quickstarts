from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Session schemas
class SessionCreate(BaseModel):
    session_id: str

class SessionResponse(BaseModel):
    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    content: str
    message_type: str

class MessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Tool run schemas
class ToolRunCreate(BaseModel):
    tool_name: str
    command: str

class ToolRunUpdate(BaseModel):
    status: str
    output: Optional[str] = None
    error: Optional[str] = None

class ToolRunResponse(BaseModel):
    id: int
    tool_name: str
    command: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Session with related data
class SessionWithData(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]
    tool_runs: List[ToolRunResponse]

    class Config:
        from_attributes = True
