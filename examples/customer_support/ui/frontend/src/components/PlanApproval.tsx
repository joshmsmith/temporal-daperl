import type { ExecutionPlan } from '../lib/api';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface PlanApprovalProps {
  plan: ExecutionPlan;
  onApprove: () => void;
  onCancel: () => void;
  approving: boolean;
}

export default function PlanApproval({ plan, onApprove, onCancel, approving }: PlanApprovalProps) {
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'green';
      case 'medium': return 'yellow';
      case 'high': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="plan-approval">
      <div className="approval-header">
        <AlertTriangle size={24} color="#ff9800" />
        <h3>Plan Approval Required</h3>
      </div>

      <div className="plan-details">
        <div className="plan-meta">
          <div className="meta-item">
            <span className="meta-label">Actions:</span>
            <span className="meta-value">{plan.actions.length}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Risk Level:</span>
            <span className={`risk-badge risk-${getRiskColor(plan.risk_level)}`}>
              {plan.risk_level}
            </span>
          </div>
          {plan.estimated_duration && (
            <div className="meta-item">
              <span className="meta-label">Est. Duration:</span>
              <span className="meta-value">{plan.estimated_duration}</span>
            </div>
          )}
        </div>

        <div className="actions-list">
          <h4>Planned Actions</h4>
          {plan.actions.map((action, index) => (
            <div key={action.id} className="action-item">
              <div className="action-number">{index + 1}</div>
              <div className="action-content">
                <div className="action-header">
                  <span className="action-type">{action.action_type}</span>
                  <span className="action-confidence">
                    Confidence: {(action.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="action-description">{action.description}</p>
                <div className="action-target">
                  <span className="target-label">Target:</span>
                  <span className="target-value">{action.target}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="approval-actions">
        <button
          onClick={onApprove}
          disabled={approving}
          className="btn-approve"
        >
          <CheckCircle size={20} />
          {approving ? 'Approving...' : 'Approve Plan'}
        </button>
        <button
          onClick={onCancel}
          disabled={approving}
          className="btn-cancel"
        >
          <XCircle size={20} />
          Cancel Workflow
        </button>
      </div>
    </div>
  );
}
