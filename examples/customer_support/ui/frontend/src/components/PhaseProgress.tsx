import type { WorkflowStatus } from '../lib/api';
import { CheckCircle, Circle, Clock, XCircle } from 'lucide-react';

interface PhaseProgressProps {
  status: WorkflowStatus;
}

interface Phase {
  name: string;
  label: string;
  icon: string;
  complete: boolean;
}

export default function PhaseProgress({ status }: PhaseProgressProps) {
  const phases: Phase[] = [
    {
      name: 'detection',
      label: 'Detection',
      icon: '🔍',
      complete: status.detection_complete,
    },
    {
      name: 'analysis',
      label: 'Analysis',
      icon: '📊',
      complete: status.analysis_complete,
    },
    {
      name: 'planning',
      label: 'Planning',
      icon: '📋',
      complete: status.planning_complete,
    },
    {
      name: 'execution',
      label: 'Execution',
      icon: '⚙️',
      complete: status.execution_complete,
    },
    {
      name: 'reporting',
      label: 'Reporting',
      icon: '📈',
      complete: status.reporting_complete,
    },
    {
      name: 'learning',
      label: 'Learning',
      icon: '🧠',
      complete: status.learning_complete,
    },
  ];

  const getPhaseStatus = (phase: Phase, index: number) => {
    if (phase.complete) return 'complete';
    if (index === 0 || phases[index - 1].complete) return 'active';
    return 'pending';
  };

  return (
    <div className="phase-progress">
      <h3>DAPERL Workflow Progress</h3>
      <div className="phases">
        {phases.map((phase, index) => {
          const phaseStatus = getPhaseStatus(phase, index);
          
          return (
            <div key={phase.name} className="phase-item">
              <div className={`phase-indicator ${phaseStatus}`}>
                {phaseStatus === 'complete' ? (
                  <CheckCircle size={24} />
                ) : phaseStatus === 'active' ? (
                  <Clock size={24} />
                ) : (
                  <Circle size={24} />
                )}
              </div>
              <div className="phase-content">
                <span className="phase-icon">{phase.icon}</span>
                <span className="phase-label">{phase.label}</span>
              </div>
              {index < phases.length - 1 && (
                <div className={`phase-connector ${phase.complete ? 'complete' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
