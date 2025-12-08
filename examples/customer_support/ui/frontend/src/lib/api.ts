/**
 * API client for communicating with the DAPERL backend
 */

const API_BASE_URL = 'http://localhost:8000';

export interface WorkflowStatus {
  status: string;
  detection_complete: boolean;
  analysis_complete: boolean;
  planning_complete: boolean;
  execution_complete: boolean;
  reporting_complete: boolean;
  learning_complete: boolean;
  plan_approved: boolean;
}

export interface Action {
  id: string;
  action_type: string;
  description: string;
  target: string;
  parameters: Record<string, any>;
  confidence: number;
  requires_approval: boolean;
}

export interface ExecutionPlan {
  id: string;
  actions: Action[];
  estimated_duration?: string;
  risk_level: string;
  requires_approval: boolean;
}

export interface Problem {
  id: string;
  type: string;
  description: string;
  severity: string;
  data: Record<string, any>;
}

export interface WorkflowResults {
  detection: {
    problems_detected: boolean;
    problems: Problem[];
    summary: string;
  } | null;
  analysis: {
    root_causes: string[];
    recommendations: string[];
    analysis_summary: string;
  } | null;
  planning: {
    plan: ExecutionPlan | null;
    planning_summary: string;
  } | null;
  execution: {
    success_count: number;
    failure_count: number;
    execution_summary: string;
  } | null;
  reporting: {
    report: string;
    metrics: Record<string, any>;
  } | null;
  learning: {
    insights: any[];
    patterns_found: number;
    learning_summary: string;
  } | null;
}

export interface WorkflowData {
  workflow_id: string;
  status: WorkflowStatus;
  plan: ExecutionPlan | null;
  results: WorkflowResults;
}

export interface CustomerSupportData {
  tickets: any[];
  customers: any[];
  product_data: any[];
  community_forums?: any[];
  knowledge_base?: any[];
  metadata?: any;
}

export interface TemporalConfig {
  ui_url: string;
  namespace: string;
  host: string;
}

export interface AppConfig {
  temporal: TemporalConfig;
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getData(): Promise<CustomerSupportData> {
    const response = await fetch(`${this.baseUrl}/api/data`);
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`);
    }
    const result = await response.json();
    return result.data;
  }

  async startWorkflow(autoApprove: boolean = false): Promise<{ workflow_id: string; success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/workflows/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ auto_approve: autoApprove }),
    });
    if (!response.ok) {
      throw new Error(`Failed to start workflow: ${response.statusText}`);
    }
    return response.json();
  }

  async getWorkflow(workflowId: string): Promise<WorkflowData> {
    const response = await fetch(`${this.baseUrl}/api/workflows/${workflowId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow: ${response.statusText}`);
    }
    return response.json();
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await fetch(`${this.baseUrl}/api/workflows/${workflowId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow status: ${response.statusText}`);
    }
    return response.json();
  }

  async getWorkflowPlan(workflowId: string): Promise<ExecutionPlan> {
    const response = await fetch(`${this.baseUrl}/api/workflows/${workflowId}/plan`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow plan: ${response.statusText}`);
    }
    return response.json();
  }

  async approvePlan(workflowId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/workflows/${workflowId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ approved: true }),
    });
    if (!response.ok) {
      throw new Error(`Failed to approve plan: ${response.statusText}`);
    }
    return response.json();
  }

  async cancelWorkflow(workflowId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/workflows/${workflowId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ approved: false }),
    });
    if (!response.ok) {
      throw new Error(`Failed to cancel workflow: ${response.statusText}`);
    }
    return response.json();
  }

  async getConfig(): Promise<AppConfig> {
    const response = await fetch(`${this.baseUrl}/api/config`);
    if (!response.ok) {
      throw new Error(`Failed to fetch config: ${response.statusText}`);
    }
    return response.json();
  }

  createWebSocket(workflowId: string): WebSocket {
    const wsUrl = this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    return new WebSocket(`${wsUrl}/ws/workflows/${workflowId}`);
  }
}

export const apiClient = new APIClient();
