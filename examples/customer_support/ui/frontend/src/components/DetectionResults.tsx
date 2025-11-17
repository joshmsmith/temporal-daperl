import type { Problem } from '../lib/api';
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';

interface DetectionResultsProps {
  data: {
    problems_detected: boolean;
    problems: Problem[];
    summary: string;
  };
}

export default function DetectionResults({ data }: DetectionResultsProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <XCircle size={20} color="#d32f2f" />;
      case 'high':
        return <AlertCircle size={20} color="#f57c00" />;
      case 'medium':
        return <AlertTriangle size={20} color="#fbc02d" />;
      case 'low':
        return <Info size={20} color="#1976d2" />;
      default:
        return <Info size={20} color="#757575" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'default';
    }
  };

  return (
    <div className="results-section">
      <h3>🔍 Detection Results</h3>
      
      {data.summary && (
        <div className="section-summary">
          <p>{data.summary}</p>
        </div>
      )}

      {data.problems_detected ? (
        <div className="problems-list">
          <h4>Problems Detected ({data.problems.length})</h4>
          {data.problems.map((problem) => (
            <div key={problem.id} className={`problem-item severity-${getSeverityColor(problem.severity)}`}>
              <div className="problem-header">
                {getSeverityIcon(problem.severity)}
                <span className="problem-type">{problem.type}</span>
                <span className={`severity-badge severity-${getSeverityColor(problem.severity)}`}>
                  {problem.severity}
                </span>
              </div>
              <p className="problem-description">{problem.description}</p>
              {Object.keys(problem.data).length > 0 && (
                <details className="problem-details">
                  <summary>Additional Data</summary>
                  <pre>{JSON.stringify(problem.data, null, 2)}</pre>
                </details>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="no-problems">
          <p>✅ No problems detected</p>
        </div>
      )}
    </div>
  );
}
