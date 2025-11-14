"""
FastAPI backend for Customer Support DAPERL Dashboard.

This server provides REST API endpoints and WebSocket support for
real-time workflow monitoring and control.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from temporalio.client import Client, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from pydantic import BaseModel

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow


# Global Temporal client
temporal_client: Optional[Client] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global temporal_client
    
    # Startup: Connect to Temporal with Pydantic v2 data converter
    temporal_config = settings.get_temporal_config()
    print(f"🔌 Connecting to Temporal at {temporal_config.host}...")
    temporal_client = await Client.connect(
        temporal_config.host,
        namespace=temporal_config.namespace,
        data_converter=pydantic_data_converter
    )
    print("✅ Connected to Temporal")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Customer Support DAPERL Dashboard API",
    description="REST API for monitoring and controlling customer support automation workflows",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ApprovalRequest(BaseModel):
    """Request to approve a workflow plan."""
    approved: bool


class WorkflowInfo(BaseModel):
    """Basic workflow information."""
    workflow_id: str
    status: str
    started_at: Optional[str] = None


# API Routes

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Customer Support DAPERL Dashboard API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/workflows")
async def list_workflows() -> List[WorkflowInfo]:
    """List all customer support workflows."""
    try:
        # Query Temporal for workflows
        # Note: This is a simplified version. In production, you'd want to
        # use Temporal's list_workflows API with proper filtering
        workflows = []
        
        # For now, we'll return an empty list as Temporal's list API
        # requires more setup. The UI can work with individual workflow IDs.
        return workflows
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get specific workflow details."""
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        
        # Query workflow status
        status = await handle.query(DAPERLWorkflow.get_status)
        
        # Query execution plan if available
        plan = None
        if status.get('planning_complete'):
            plan = await handle.query(DAPERLWorkflow.get_plan)
        
        # Query all results
        results = await handle.query(DAPERLWorkflow.get_results)
        
        return {
            "workflow_id": workflow_id,
            "status": status,
            "plan": plan,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {str(e)}")


@app.get("/api/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get workflow status only (lighter query)."""
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        status = await handle.query(DAPERLWorkflow.get_status)
        return status
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {str(e)}")


@app.get("/api/workflows/{workflow_id}/plan")
async def get_workflow_plan(workflow_id: str) -> Dict[str, Any]:
    """Get workflow execution plan."""
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        plan = await handle.query(DAPERLWorkflow.get_plan)
        
        if not plan:
            raise HTTPException(status_code=404, detail="No plan available yet")
        
        return plan
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/workflows/{workflow_id}/results")
async def get_workflow_results(workflow_id: str) -> Dict[str, Any]:
    """Get all workflow phase results."""
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        results = await handle.query(DAPERLWorkflow.get_results)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/workflows/{workflow_id}/approve")
async def approve_plan(workflow_id: str, request: ApprovalRequest) -> Dict[str, Any]:
    """Approve or reject the execution plan."""
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        
        if request.approved:
            # Send approval signal using the signal name as a string
            await handle.signal("approve_plan")
            return {
                "success": True,
                "message": "Plan approved successfully"
            }
        else:
            # Send cancel signal using the signal name as a string
            await handle.signal("cancel_workflow")
            return {
                "success": True,
                "message": "Workflow cancelled"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve plan: {str(e)}")


@app.websocket("/ws/workflows/{workflow_id}")
async def workflow_updates(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow updates."""
    await websocket.accept()
    
    try:
        handle: WorkflowHandle = temporal_client.get_workflow_handle(workflow_id)
        
        # Send updates every 2 seconds
        while True:
            try:
                status = await handle.query(DAPERLWorkflow.get_status)
                
                # Send status update
                await websocket.send_json({
                    "type": "status_update",
                    "data": status,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # If workflow is completed or failed, we can stop polling
                if status.get('status') in ['COMPLETED', 'FAILED', 'CANCELLED']:
                    break
                
                await asyncio.sleep(2)
            
            except Exception as e:
                # If workflow doesn't exist or query fails, send error and close
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                break
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for workflow {workflow_id}")
    except Exception as e:
        print(f"WebSocket error for workflow {workflow_id}: {e}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    temporal_connected = temporal_client is not None
    
    return {
        "status": "healthy" if temporal_connected else "unhealthy",
        "temporal_connected": temporal_connected,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
