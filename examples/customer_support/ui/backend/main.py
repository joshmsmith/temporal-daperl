"""
FastAPI backend for Customer Support DAPERL Dashboard.

This server provides REST API endpoints and WebSocket support for
real-time workflow monitoring and control.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from temporalio.client import Client, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from pydantic import BaseModel

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow
from daperl.core.models import DAPERLInput


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


class StartWorkflowRequest(BaseModel):
    """Request to start a new workflow."""
    auto_approve: bool = False
    workflow_id: Optional[str] = None


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
        workflows = []
        
        # Query Temporal for workflows using list_workflows API
        async for workflow in temporal_client.list_workflows(
            query="WorkflowType='DAPERLWorkflow'"
        ):
            # Get workflow execution info
            workflow_info = WorkflowInfo(
                workflow_id=workflow.id,
                status=workflow.status.name,
                started_at=workflow.start_time.isoformat() if workflow.start_time else None
            )
            workflows.append(workflow_info)
        
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


@app.get("/api/data")
async def get_customer_support_data() -> Dict[str, Any]:
    """Get customer support data from data.json file."""
    try:
        # Path to data.json (three levels up from backend directory to get to examples/customer_support/)
        data_path = Path(__file__).parent.parent.parent / "data.json"
        
        if not data_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file not found at {data_path}")
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Extract the nested customer support data
        support_data = data.get("customer_support_data", data)
        
        return {
            "data": support_data,
            "loaded_at": datetime.utcnow().isoformat(),
            "source": str(data_path)
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in data file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/start")
async def start_workflow(request: StartWorkflowRequest) -> Dict[str, Any]:
    """Start a new DAPERL workflow with customer support data."""
    try:
        # Load customer support data
        data_path = Path(__file__).parent.parent.parent / "data.json"
        
        if not data_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file not found at {data_path}")
        
        with open(data_path, 'r') as f:
            all_data = json.load(f)
        
        # Extract the nested customer support data
        support_data = all_data.get("customer_support_data", all_data)
        
        # Add metadata
        enhanced_data = {
            **support_data,
            "workflow_metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "total_tickets": len(support_data.get('tickets', [])),
                "auto_approve_enabled": request.auto_approve,
                "started_from_ui": True
            }
        }
        
        # Configuration for customer support domain (similar to run_example.py)
        config = {
            "detection_instructions": "Analyze customer support data and detect critical issues including SLA violations, customer sentiment issues, account health risks, knowledge gaps, and operational issues.",
            "analysis_instructions": "Conduct deep customer context analysis including customer profile analysis, churn risk assessment, technical complexity evaluation, and organizational impact.",
            "planning_instructions": "Create intelligent customer support response strategies with appropriate escalation workflows, communication planning, and resource allocation.",
            "reporting_instructions": "Generate comprehensive customer support performance analytics including SLA performance, customer health metrics, operational efficiency, and quality metrics.",
            "learning_instructions": "Extract strategic insights for continuous customer support improvement through pattern discovery, predictive intelligence, and process optimization.",
            "available_actions": [
                "update_ticket_status",
                "send_customer_response",
                "update_customer_account",
                "search_knowledge_base",
                "escalate_to_specialist",
                "notify_account_manager",
                "create_follow_up_task"
            ],
            "domain_specific_config": {
                "sla_monitoring": True,
                "sentiment_analysis": True,
                "churn_prediction": True,
                "auto_escalation": True,
                "knowledge_base_integration": True
            }
        }
        
        # Create workflow input
        workflow_input = DAPERLInput(
            domain="customer-support",
            data=enhanced_data,
            config=config,
            auto_approve=request.auto_approve,
            metadata={
                "example": "customer_support",
                "processing_mode": "auto" if request.auto_approve else "manual",
                "started_from": "ui"
            }
        )
        
        # Generate workflow ID if not provided
        if request.workflow_id:
            workflow_id = request.workflow_id
        else:
            workflow_id = f"customer-support-{int(datetime.now().timestamp())}"
        
        # Get Temporal configuration
        temporal_config = settings.get_temporal_config()
        
        # Start workflow
        handle = await temporal_client.start_workflow(
            DAPERLWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow started successfully",
            "auto_approve": request.auto_approve,
            "started_at": datetime.utcnow().isoformat()
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in data file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")


@app.get("/api/config")
async def get_config():
    """Get configuration for the frontend."""
    temporal_config = settings.get_temporal_config()
    
    # Construct Temporal UI URL based on host
    temporal_host = temporal_config.host
    # Extract just the hostname (remove port if present)
    host_parts = temporal_host.split(':')
    temporal_ui_host = host_parts[0]
    
    # Default to port 8233 for Temporal UI
    temporal_ui_url = f"http://{temporal_ui_host}:8233"
    
    return {
        "temporal": {
            "ui_url": temporal_ui_url,
            "namespace": temporal_config.namespace,
            "host": temporal_config.host
        }
    }


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
