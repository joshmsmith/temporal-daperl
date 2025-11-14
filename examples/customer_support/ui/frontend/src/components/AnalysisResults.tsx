interface AnalysisResultsProps {
  data: {
    root_causes: string[];
    recommendations: string[];
    analysis_summary: string;
  };
}

export default function AnalysisResults({ data }: AnalysisResultsProps) {
  return (
    <div className="results-section">
      <h3>📊 Analysis Results</h3>
      
      {data.analysis_summary && (
        <div className="section-summary">
          <p>{data.analysis_summary}</p>
        </div>
      )}

      {data.root_causes && data.root_causes.length > 0 && (
        <div className="subsection">
          <h4>Root Causes</h4>
          <ul className="list-items">
            {data.root_causes.map((cause, index) => (
              <li key={index}>{cause}</li>
            ))}
          </ul>
        </div>
      )}

      {data.recommendations && data.recommendations.length > 0 && (
        <div className="subsection">
          <h4>Recommendations</h4>
          <ul className="list-items">
            {data.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
