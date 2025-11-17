import { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard.tsx';
import DataOverview from './components/DataOverview.tsx';

// Default workflow ID for customer support example
const DEFAULT_WORKFLOW_ID = 'customer-support-demo';

type View = 'data' | 'workflow';

function App() {
  const [currentView, setCurrentView] = useState<View>('data');
  const [workflowId, setWorkflowId] = useState(DEFAULT_WORKFLOW_ID);
  const [inputWorkflowId, setInputWorkflowId] = useState(DEFAULT_WORKFLOW_ID);

  const handleWorkflowIdSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setWorkflowId(inputWorkflowId);
    setCurrentView('workflow');
  };

  const handleWorkflowStarted = (newWorkflowId: string) => {
    setWorkflowId(newWorkflowId);
    setInputWorkflowId(newWorkflowId);
    setCurrentView('workflow');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎧 Customer Support DAPERL Dashboard</h1>
            <p className="subtitle">Intelligent Support Automation Monitoring</p>
          </div>
          
          <form onSubmit={handleWorkflowIdSubmit} className="workflow-selector">
            <input
              type="text"
              value={inputWorkflowId}
              onChange={(e) => setInputWorkflowId(e.target.value)}
              placeholder="Enter workflow ID"
              className="workflow-input"
            />
            <button type="submit" className="btn-primary">
              Load Workflow
            </button>
          </form>
        </div>
      </header>

      {/* Navigation */}
      <nav className="view-navigation">
        <button
          className={`nav-button ${currentView === 'data' ? 'active' : ''}`}
          onClick={() => setCurrentView('data')}
        >
          📊 View Data & Start Workflow
        </button>
        <button
          className={`nav-button ${currentView === 'workflow' ? 'active' : ''}`}
          onClick={() => setCurrentView('workflow')}
        >
          🔄 Monitor Workflow
        </button>
      </nav>

      <main className="app-main">
        {currentView === 'data' ? (
          <DataOverview onWorkflowStarted={handleWorkflowStarted} />
        ) : (
          <Dashboard workflowId={workflowId} />
        )}
      </main>

      <footer className="app-footer">
        <p>DAPERL Framework - Detection, Analysis, Planning, Execution, Reporting, Learning</p>
      </footer>
    </div>
  );
}

export default App;
