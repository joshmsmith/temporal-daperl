import { useState, useEffect } from 'react';
import { AlertCircle, AlertTriangle, Info, XCircle, CheckCircle, ArrowRight, ExternalLink } from 'lucide-react';
import { apiClient } from '../lib/api';
import type { Problem, WorkflowResults, CustomerSupportData } from '../lib/api';

interface ImpactAnalysisProps {
  workflowId: string;
}

interface AffectedDataItem {
  type: 'ticket' | 'customer' | 'product' | 'kb_article';
  id: string;
  label: string;
  details?: any;
}

interface ProblemWithAffectedData {
  problem: Problem;
  affectedItems: AffectedDataItem[];
}

interface ResolutionAction {
  action: string;
  target: string;
  description: string;
  success: boolean;
  affectedItems: AffectedDataItem[];
}

const ImpactAnalysis = ({ workflowId }: ImpactAnalysisProps) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<WorkflowResults | null>(null);
  const [data, setData] = useState<CustomerSupportData | null>(null);
  const [problemsWithData, setProblemsWithData] = useState<ProblemWithAffectedData[]>([]);
  const [resolutions, setResolutions] = useState<ResolutionAction[]>([]);
  const [expandedProblems, setExpandedProblems] = useState<Set<string>>(new Set());
  const [expandedResolutions, setExpandedResolutions] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadData();
  }, [workflowId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load workflow results and original data in parallel
      const [workflowData, customerData] = await Promise.all([
        apiClient.getWorkflow(workflowId),
        apiClient.getData()
      ]);

      setResults(workflowData.results);
      setData(customerData);

      // Parse problems and find affected data
      if (workflowData.results.detection?.problems) {
        const parsedProblems = parseProblemsWithData(
          workflowData.results.detection.problems,
          customerData
        );
        setProblemsWithData(parsedProblems);
      }

      // Parse execution actions and find affected data
      if (workflowData.results.execution && workflowData.plan?.actions) {
        const parsedResolutions = parseResolutions(
          workflowData.plan.actions,
          customerData
        );
        setResolutions(parsedResolutions);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load impact analysis');
    } finally {
      setLoading(false);
    }
  };

  const parseProblemsWithData = (
    problems: Problem[],
    customerData: CustomerSupportData
  ): ProblemWithAffectedData[] => {
    return problems.map(problem => {
      const affectedItems: AffectedDataItem[] = [];

      // Extract IDs from problem data
      const dataStr = JSON.stringify(problem.data);
      const descStr = problem.description;
      const fullText = `${dataStr} ${descStr}`;

      // Find ticket references
      const ticketMatches = fullText.match(/CS-\d{4}-\d{3}/g);
      if (ticketMatches) {
        ticketMatches.forEach(ticketId => {
          const ticket = customerData.tickets?.find((t: any) => t.ticket_id === ticketId);
          if (ticket && !affectedItems.find(item => item.id === ticketId)) {
            affectedItems.push({
              type: 'ticket',
              id: ticketId,
              label: ticket.subject,
              details: ticket
            });
          }
        });
      }

      // Find customer references
      const customerMatches = fullText.match(/CUST-\d{5}/g);
      if (customerMatches) {
        customerMatches.forEach(customerId => {
          const customer = customerData.customers?.find((c: any) => c.customer_id === customerId);
          if (customer && !affectedItems.find(item => item.id === customerId)) {
            affectedItems.push({
              type: 'customer',
              id: customerId,
              label: customer.company,
              details: customer
            });
          }
        });
      }

      // Check if problem data has direct references
      if (problem.data.ticket_id) {
        const ticket = customerData.tickets?.find((t: any) => t.ticket_id === problem.data.ticket_id);
        if (ticket && !affectedItems.find(item => item.id === problem.data.ticket_id)) {
          affectedItems.push({
            type: 'ticket',
            id: problem.data.ticket_id,
            label: ticket.subject,
            details: ticket
          });
        }
      }

      if (problem.data.customer_id) {
        const customer = customerData.customers?.find((c: any) => c.customer_id === problem.data.customer_id);
        if (customer && !affectedItems.find(item => item.id === problem.data.customer_id)) {
          affectedItems.push({
            type: 'customer',
            id: problem.data.customer_id,
            label: customer.company,
            details: customer
          });
        }
      }

      return { problem, affectedItems };
    });
  };

  const parseResolutions = (
    actions: any[],
    customerData: CustomerSupportData
  ): ResolutionAction[] => {
    return actions.map(action => {
      const affectedItems: AffectedDataItem[] = [];
      
      // Parse target and parameters for data references
      const targetStr = action.target || '';
      const paramsStr = JSON.stringify(action.parameters || {});
      const fullText = `${targetStr} ${paramsStr} ${action.description}`;

      // Find ticket references
      const ticketMatches = fullText.match(/CS-\d{4}-\d{3}/g);
      if (ticketMatches) {
        ticketMatches.forEach(ticketId => {
          const ticket = customerData.tickets?.find((t: any) => t.ticket_id === ticketId);
          if (ticket && !affectedItems.find(item => item.id === ticketId)) {
            affectedItems.push({
              type: 'ticket',
              id: ticketId,
              label: ticket.subject,
              details: ticket
            });
          }
        });
      }

      // Find customer references
      const customerMatches = fullText.match(/CUST-\d{5}/g);
      if (customerMatches) {
        customerMatches.forEach(customerId => {
          const customer = customerData.customers?.find((c: any) => c.customer_id === customerId);
          if (customer && !affectedItems.find(item => item.id === customerId)) {
            affectedItems.push({
              type: 'customer',
              id: customerId,
              label: customer.company,
              details: customer
            });
          }
        });
      }

      return {
        action: action.action_type,
        target: action.target,
        description: action.description,
        success: true, // Default to true, could be enhanced with actual execution results
        affectedItems
      };
    });
  };

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

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'ticket': return '🎫';
      case 'customer': return '👤';
      case 'product': return '📦';
      case 'kb_article': return '📚';
      default: return '📄';
    }
  };

  const toggleProblemExpansion = (problemId: string) => {
    const newExpanded = new Set(expandedProblems);
    if (newExpanded.has(problemId)) {
      newExpanded.delete(problemId);
    } else {
      newExpanded.add(problemId);
    }
    setExpandedProblems(newExpanded);
  };

  const toggleResolutionExpansion = (index: number) => {
    const key = `resolution-${index}`;
    const newExpanded = new Set(expandedResolutions);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedResolutions(newExpanded);
  };

  if (loading) {
    return (
      <div className="impact-analysis-loading">
        <div className="spinner"></div>
        <p>Loading impact analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="impact-analysis-error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={loadData} className="btn-primary">Retry</button>
      </div>
    );
  }

  const hasProblems = problemsWithData.length > 0;
  const hasResolutions = resolutions.length > 0;
  const executionComplete = results?.execution !== null;

  return (
    <div className="impact-analysis">
      <div className="impact-header">
        <h2>📍 Impact Analysis</h2>
        <p className="subtitle">Visual mapping of detected problems and applied resolutions</p>
      </div>

      {/* Summary Stats */}
      <div className="impact-stats">
        <div className="stat-card-impact problems">
          <div className="stat-icon">🔍</div>
          <div className="stat-content">
            <div className="stat-value">{problemsWithData.length}</div>
            <div className="stat-label">Problems Detected</div>
          </div>
        </div>
        <div className="stat-card-impact items">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">
              {problemsWithData.reduce((sum, p) => sum + p.affectedItems.length, 0)}
            </div>
            <div className="stat-label">Affected Items</div>
          </div>
        </div>
        <div className="stat-card-impact resolutions">
          <div className="stat-icon">⚙️</div>
          <div className="stat-content">
            <div className="stat-value">{resolutions.length}</div>
            <div className="stat-label">Actions Applied</div>
          </div>
        </div>
      </div>

      {/* Problems Section */}
      <div className="impact-section">
        <h3>🔍 Detected Problems & Affected Data</h3>
        {!hasProblems ? (
          <div className="no-data">
            <p>✅ No problems detected in this workflow</p>
          </div>
        ) : (
          <div className="problems-impact-list">
            {problemsWithData.map((item) => {
              const isExpanded = expandedProblems.has(item.problem.id);
              return (
                <div
                  key={item.problem.id}
                  className={`problem-impact-card severity-${getSeverityColor(item.problem.severity)}`}
                >
                  <div
                    className="problem-impact-header"
                    onClick={() => toggleProblemExpansion(item.problem.id)}
                  >
                    <div className="problem-impact-title">
                      {getSeverityIcon(item.problem.severity)}
                      <span className="problem-type">{item.problem.type}</span>
                      <span className={`severity-badge severity-${getSeverityColor(item.problem.severity)}`}>
                        {item.problem.severity}
                      </span>
                    </div>
                    <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                  </div>
                  
                  <p className="problem-description">{item.problem.description}</p>
                  
                  {item.affectedItems.length > 0 && (
                    <div className="affected-items">
                      <h4>Affected Items ({item.affectedItems.length})</h4>
                      <div className="affected-items-grid">
                        {item.affectedItems.map((dataItem) => (
                          <div key={dataItem.id} className={`affected-item ${dataItem.type}`}>
                            <span className="item-icon">{getItemIcon(dataItem.type)}</span>
                            <div className="item-info">
                              <div className="item-id">{dataItem.id}</div>
                              <div className="item-label">{dataItem.label}</div>
                              {dataItem.details && isExpanded && (
                                <div className="item-details">
                                  {dataItem.type === 'ticket' && (
                                    <>
                                      <span className={`priority-badge priority-${dataItem.details.priority}`}>
                                        {dataItem.details.priority}
                                      </span>
                                      <span className={`status-badge-small status-${dataItem.details.status}`}>
                                        {dataItem.details.status}
                                      </span>
                                    </>
                                  )}
                                  {dataItem.type === 'customer' && (
                                    <>
                                      <span className="detail-badge">
                                        {dataItem.details.plan}
                                      </span>
                                      <span className={`health-badge health-${dataItem.details.health_score}`}>
                                        {dataItem.details.health_score}
                                      </span>
                                    </>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Resolutions Section */}
      {executionComplete && (
        <div className="impact-section">
          <h3>⚙️ Applied Resolutions</h3>
          {!hasResolutions ? (
            <div className="no-data">
              <p>No resolutions applied yet</p>
            </div>
          ) : (
            <div className="resolutions-list">
              {resolutions.map((resolution, index) => {
                const key = `resolution-${index}`;
                const isExpanded = expandedResolutions.has(key);
                return (
                  <div key={key} className="resolution-card">
                    <div
                      className="resolution-header"
                      onClick={() => toggleResolutionExpansion(index)}
                    >
                      <div className="resolution-title">
                        {resolution.success ? (
                          <CheckCircle size={20} color="#2e7d32" />
                        ) : (
                          <XCircle size={20} color="#d32f2f" />
                        )}
                        <span className="action-type">{resolution.action}</span>
                        <ArrowRight size={16} className="arrow-icon" />
                        <span className="action-target">{resolution.target}</span>
                      </div>
                      <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                    </div>
                    
                    <p className="resolution-description">{resolution.description}</p>
                    
                    {resolution.affectedItems.length > 0 && (
                      <div className="affected-items">
                        <h4>Modified Items ({resolution.affectedItems.length})</h4>
                        <div className="affected-items-grid">
                          {resolution.affectedItems.map((dataItem) => (
                            <div key={dataItem.id} className={`affected-item ${dataItem.type}`}>
                              <span className="item-icon">{getItemIcon(dataItem.type)}</span>
                              <div className="item-info">
                                <div className="item-id">{dataItem.id}</div>
                                <div className="item-label">{dataItem.label}</div>
                                {dataItem.details && isExpanded && (
                                  <div className="item-details">
                                    {dataItem.type === 'ticket' && (
                                      <>
                                        <span className={`priority-badge priority-${dataItem.details.priority}`}>
                                          {dataItem.details.priority}
                                        </span>
                                        <span className={`status-badge-small status-${dataItem.details.status}`}>
                                          {dataItem.details.status}
                                        </span>
                                      </>
                                    )}
                                    {dataItem.type === 'customer' && (
                                      <>
                                        <span className="detail-badge">
                                          {dataItem.details.plan}
                                        </span>
                                        <span className={`health-badge health-${dataItem.details.health_score}`}>
                                          {dataItem.details.health_score}
                                        </span>
                                      </>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {!executionComplete && hasProblems && (
        <div className="info-message">
          <Info size={20} />
          <p>Resolutions will appear here after the execution phase completes</p>
        </div>
      )}
    </div>
  );
};

export default ImpactAnalysis;
