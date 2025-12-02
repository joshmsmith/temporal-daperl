import { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard.tsx';
import DataOverview from './components/DataOverview.tsx';
import ImpactAnalysis from './components/ImpactAnalysis.tsx';

// Default workflow ID for customer support example
const DEFAULT_WORKFLOW_ID = 'customer-support-demo';

type View = 'data' | 'workflow' | 'impact';

interface WorkflowInfo {
  workflow_id: string;
  status: string;
  started_at: string | null;
}

function App() {
  const [currentView, setCurrentView] = useState<View>('data');
  const [workflowId, setWorkflowId] = useState(DEFAULT_WORKFLOW_ID);
  const [inputWorkflowId, setInputWorkflowId] = useState(DEFAULT_WORKFLOW_ID);
  const [availableWorkflows, setAvailableWorkflows] = useState<WorkflowInfo[]>([]);
  const [loadingWorkflows, setLoadingWorkflows] = useState(true);

  // Fetch available workflows on component mount
  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/workflows');
        if (response.ok) {
          const workflows = await response.json();
          setAvailableWorkflows(workflows);
          
          // If workflows exist and we have the default ID, check if it exists
          if (workflows.length > 0) {
            const defaultExists = workflows.some((w: WorkflowInfo) => w.workflow_id === DEFAULT_WORKFLOW_ID);
            if (!defaultExists) {
              // Use the first available workflow
              setInputWorkflowId(workflows[0].workflow_id);
              setWorkflowId(workflows[0].workflow_id);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch workflows:', error);
      } finally {
        setLoadingWorkflows(false);
      }
    };

    fetchWorkflows();
    
    // Refresh workflow list every 10 seconds
    const interval = setInterval(fetchWorkflows, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleWorkflowIdSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setWorkflowId(inputWorkflowId);
    setCurrentView('workflow');
  };

  const handleWorkflowStarted = (newWorkflowId: string) => {
    setWorkflowId(newWorkflowId);
    setInputWorkflowId(newWorkflowId);
    setCurrentView('workflow');
    
    // Refresh workflow list when a new workflow is started
    fetch('http://localhost:8000/api/workflows')
      .then(res => res.json())
      .then(workflows => setAvailableWorkflows(workflows))
      .catch(err => console.error('Failed to refresh workflows:', err));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎧 Customer Support DAPERL Dashboard</h1>
            <p className="subtitle">Intelligent Support Automation Monitoring</p>
          </div>
          
          {!loadingWorkflows && availableWorkflows.length > 0 && (
            <form onSubmit={handleWorkflowIdSubmit} className="workflow-selector">
              <select
                value={inputWorkflowId}
                onChange={(e) => setInputWorkflowId(e.target.value)}
                className="workflow-input"
              >
                {availableWorkflows.map((workflow) => (
                  <option key={workflow.workflow_id} value={workflow.workflow_id}>
                    {workflow.workflow_id} ({workflow.status})
                  </option>
                ))}
              </select>
              <button type="submit" className="btn-primary">
                Load Workflow
              </button>
            </form>
          )}
        </div>
      </header>

      {/* Navigation */}
      <nav className="view-navigation">
        <button
          className={`nav-button ${currentView === 'data' ? 'active' : ''}`}
          onClick={() => setCurrentView('data')}
        >
          📊 Peep the Data & Boot the Workflow
        </button>
        <button
          className={`nav-button ${currentView === 'workflow' ? 'active' : ''}`}
          onClick={() => setCurrentView('workflow')}
        >
          🔄 Workflow - On the Air
        </button>
        <button
          className={`nav-button ${currentView === 'impact' ? 'active' : ''}`}
          onClick={() => setCurrentView('impact')}
        >
          📍 Dude, what happened?
        </button>
      </nav>

      <main className="app-main">
        {currentView === 'data' ? (
          <DataOverview onWorkflowStarted={handleWorkflowStarted} />
        ) : currentView === 'workflow' ? (
          <Dashboard workflowId={workflowId} />
        ) : (
          <ImpactAnalysis workflowId={workflowId} />
        )}
      </main>

      <footer className="app-footer">
        <p>DAPERL Framework - Detection, Analysis, Planning, Execution, Reporting, Learning</p>
      </footer>
    </div>
  );
}

export default App;
