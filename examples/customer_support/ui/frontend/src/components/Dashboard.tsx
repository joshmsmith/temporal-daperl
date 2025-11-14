import { useState, useEffect, useRef } from 'react';
import { apiClient, type WorkflowData, type WorkflowStatus } from '../lib/api';
import PhaseProgress from './PhaseProgress.tsx';
import PlanApproval from './PlanApproval.tsx';
import DetectionResults from './DetectionResults.tsx';
import AnalysisResults from './AnalysisResults.tsx';
import ExecutionResults from './ExecutionResults.tsx';
import ReportingResults from './ReportingResults.tsx';

interface DashboardProps {
  workflowId: string;
}

export default function Dashboard({ workflowId }: DashboardProps) {
  const [workflow, setWorkflow] = useState<WorkflowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);
  const [loadTimestamp, setLoadTimestamp] = useState<number>(0);
  const workflowRef = useRef<WorkflowData | null>(null);
  
  // Keep ref in sync with state
  useEffect(() => {
    workflowRef.current = workflow;
  }, [workflow]);

  // Fetch workflow data
  useEffect(() => {
    const fetchWorkflow = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getWorkflow(workflowId);
        setWorkflow(data);
        // Update load timestamp to trigger WebSocket reconnection
        setLoadTimestamp(Date.now());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workflow');
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflow();
  }, [workflowId]);

  // Set up WebSocket for real-time updates
  useEffect(() => {
    // Only connect WebSocket after initial workflow load
    if (!workflow) {
      console.log('Workflow not loaded yet, skipping WebSocket setup');
      return;
    }
    
    // Skip WebSocket for workflows in terminal states (they won't update)
    const status = workflow.status.status;
    if (status === 'COMPLETED' || status === 'FAILED' || status === 'CANCELLED') {
      console.log(`Workflow in terminal state (${status}), skipping WebSocket setup`);
      return;
    }

    console.log('Setting up WebSocket for workflow:', workflowId, 'Status:', status);
    const ws = apiClient.createWebSocket(workflowId);

    ws.onopen = () => {
      console.log('✓ WebSocket connected for workflow:', workflowId);
    };

    ws.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'status_update') {
          const newStatus = message.data as WorkflowStatus;
          const currentWorkflow = workflowRef.current;
          
          if (!currentWorkflow) {
            console.log('No current workflow in ref, skipping update');
            return;
          }
          
          // Check if status has actually changed from what we have
          const hasStatusChanged = currentWorkflow.status.status !== newStatus.status;
          const hasPhaseCompleted = 
            (newStatus.detection_complete && !currentWorkflow.status.detection_complete) ||
            (newStatus.analysis_complete && !currentWorkflow.status.analysis_complete) ||
            (newStatus.planning_complete && !currentWorkflow.status.planning_complete) ||
            (newStatus.execution_complete && !currentWorkflow.status.execution_complete) ||
            (newStatus.reporting_complete && !currentWorkflow.status.reporting_complete) ||
            (newStatus.learning_complete && !currentWorkflow.status.learning_complete) ||
            (newStatus.plan_approved && !currentWorkflow.status.plan_approved);
          
          // If status changed or a phase completed, refetch full workflow data
          if (hasStatusChanged || hasPhaseCompleted) {
            console.log('🔄 Status changed or phase completed, refetching full workflow data');
            console.log('  Old status:', currentWorkflow.status.status, '→ New status:', newStatus.status);
            console.log('  Phase changes:', {
              detection: newStatus.detection_complete !== currentWorkflow.status.detection_complete,
              analysis: newStatus.analysis_complete !== currentWorkflow.status.analysis_complete,
              planning: newStatus.planning_complete !== currentWorkflow.status.planning_complete,
              execution: newStatus.execution_complete !== currentWorkflow.status.execution_complete,
              reporting: newStatus.reporting_complete !== currentWorkflow.status.reporting_complete,
              learning: newStatus.learning_complete !== currentWorkflow.status.learning_complete,
              approved: newStatus.plan_approved !== currentWorkflow.status.plan_approved,
            });
            
            try {
              const updatedWorkflow = await apiClient.getWorkflow(workflowId);
              console.log('✓ Successfully refetched workflow data');
              setWorkflow(updatedWorkflow);
            } catch (err) {
              console.error('✗ Failed to refetch workflow data:', err);
              // Fall back to just updating status
              setWorkflow((prev) => {
                if (!prev) return prev;
                return {
                  ...prev,
                  status: newStatus,
                };
              });
            }
          } else {
            // Just update status if nothing significant changed
            console.log('📊 Updating status only (no significant changes)');
            setWorkflow((prev) => {
              if (!prev) return prev;
              return {
                ...prev,
                status: newStatus,
              };
            });
          }
          
          // Close WebSocket if workflow is now in terminal state
          if (newStatus.status === 'COMPLETED' || newStatus.status === 'FAILED' || newStatus.status === 'CANCELLED') {
            console.log('🏁 Workflow in terminal state, closing WebSocket');
            ws.close();
          }
        } else if (message.type === 'error') {
          console.error('WebSocket error message:', message.message);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket connection error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected for workflow:', workflowId);
    };

    return () => {
      console.log('🧹 Cleaning up WebSocket for workflow:', workflowId);
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [workflowId, loadTimestamp]); // Depend on workflowId and when workflow was loaded

  const handleApprovePlan = async () => {
    try {
      setApproving(true);
      await apiClient.approvePlan(workflowId);
      
      // Wait a bit for the signal to be processed, then reload
      // The WebSocket will also trigger updates, but we want immediate feedback
      await new Promise(resolve => setTimeout(resolve, 500));
      const data = await apiClient.getWorkflow(workflowId);
      setWorkflow(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve plan');
    } finally {
      setApproving(false);
    }
  };

  const handleCancelWorkflow = async () => {
    try {
      setApproving(true);
      await apiClient.cancelWorkflow(workflowId);
      
      // Wait a bit for the signal to be processed, then reload
      await new Promise(resolve => setTimeout(resolve, 500));
      const data = await apiClient.getWorkflow(workflowId);
      setWorkflow(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel workflow');
    } finally {
      setApproving(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading workflow data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="btn-primary">
          Retry
        </button>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="dashboard-error">
        <h2>No workflow data available</h2>
      </div>
    );
  }

  const isPendingApproval = workflow.status.status === 'PENDING_APPROVAL';
  const isCompleted = workflow.status.status === 'COMPLETED';
  const isFailed = workflow.status.status === 'FAILED';
  const isCancelled = workflow.status.status === 'CANCELLED';

  return (
    <div className="dashboard">
      {/* Workflow Status Header */}
      <div className="status-header">
        <div className="status-info">
          <h2>Workflow: {workflow.workflow_id}</h2>
          <div className={`status-badge status-${workflow.status.status.toLowerCase()}`}>
            {workflow.status.status}
          </div>
        </div>
      </div>

      {/* DAPERL Phase Progress */}
      <PhaseProgress status={workflow.status} />

      {/* Plan Approval Section */}
      {isPendingApproval && workflow.plan && (
        <PlanApproval
          plan={workflow.plan}
          onApprove={handleApprovePlan}
          onCancel={handleCancelWorkflow}
          approving={approving}
        />
      )}

      {/* Results Sections */}
      <div className="results-container">
        {workflow.results.detection && (
          <DetectionResults data={workflow.results.detection} />
        )}

        {workflow.results.analysis && (
          <AnalysisResults data={workflow.results.analysis} />
        )}

        {workflow.results.execution && (
          <ExecutionResults data={workflow.results.execution} />
        )}

        {workflow.results.reporting && (
          <ReportingResults data={workflow.results.reporting} />
        )}
      </div>

      {/* Final Status Message */}
      {isCompleted && (
        <div className="status-message success">
          <h3>✅ Workflow Completed Successfully</h3>
          <p>All phases completed. Check results above for details.</p>
        </div>
      )}

      {isFailed && (
        <div className="status-message error">
          <h3>❌ Workflow Failed</h3>
          <p>The workflow encountered an error. Check the logs for details.</p>
        </div>
      )}

      {isCancelled && (
        <div className="status-message warning">
          <h3>⚠️ Workflow Cancelled</h3>
          <p>The workflow was cancelled by user request.</p>
        </div>
      )}
    </div>
  );
}
