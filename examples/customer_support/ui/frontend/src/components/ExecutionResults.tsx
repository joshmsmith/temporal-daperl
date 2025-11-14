import { CheckCircle, XCircle } from 'lucide-react';

interface ExecutionResultsProps {
  data: {
    success_count: number;
    failure_count: number;
    execution_summary: string;
  };
}

export default function ExecutionResults({ data }: ExecutionResultsProps) {
  const total = data.success_count + data.failure_count;
  const successRate = total > 0 ? ((data.success_count / total) * 100).toFixed(1) : 0;

  return (
    <div className="results-section">
      <h3>⚙️ Execution Results</h3>
      
      {data.execution_summary && (
        <div className="section-summary">
          <p>{data.execution_summary}</p>
        </div>
      )}

      <div className="execution-stats">
        <div className="stat-card success">
          <CheckCircle size={32} />
          <div className="stat-content">
            <div className="stat-value">{data.success_count}</div>
            <div className="stat-label">Successful</div>
          </div>
        </div>
        
        <div className="stat-card failure">
          <XCircle size={32} />
          <div className="stat-content">
            <div className="stat-value">{data.failure_count}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>

        <div className="stat-card total">
          <div className="stat-content">
            <div className="stat-value">{successRate}%</div>
            <div className="stat-label">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}
