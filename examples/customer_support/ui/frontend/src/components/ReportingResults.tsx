interface ReportingResultsProps {
  data: {
    report: string;
    metrics: Record<string, any>;
  };
}

export default function ReportingResults({ data }: ReportingResultsProps) {
  return (
    <div className="results-section">
      <h3>📈 Reporting Results</h3>
      
      {data.report && (
        <div className="section-summary">
          <p>{data.report}</p>
        </div>
      )}

      {data.metrics && Object.keys(data.metrics).length > 0 && (
        <div className="subsection">
          <h4>Metrics</h4>
          <div className="metrics-grid">
            {Object.entries(data.metrics).map(([key, value]) => (
              <div key={key} className="metric-item">
                <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                <div className="metric-value">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
