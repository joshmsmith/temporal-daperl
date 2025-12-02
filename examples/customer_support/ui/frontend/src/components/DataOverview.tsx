import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import type { CustomerSupportData } from '../lib/api';

interface DataOverviewProps {
  onWorkflowStarted: (workflowId: string) => void;
}

type SortField = 'ticket_id' | 'subject' | 'customer_id' | 'support_tier' | 'priority' | 'status' | 'category' | 'assigned_to';
type CustomerSortField = 'company' | 'customer_id' | 'plan' | 'satisfaction_score' | 'health_score';
type SortDirection = 'asc' | 'desc';

const DataOverview = ({ onWorkflowStarted }: DataOverviewProps) => {
  const [data, setData] = useState<CustomerSupportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [autoApprove, setAutoApprove] = useState(false);
  const [expandedTickets, setExpandedTickets] = useState<Set<string>>(new Set());
  const [expandedCustomers, setExpandedCustomers] = useState<Set<string>>(new Set());
  const [productsExpanded, setProductsExpanded] = useState(false);
  const [sortField, setSortField] = useState<SortField>('ticket_id');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [customerSortField, setCustomerSortField] = useState<CustomerSortField>('company');
  const [customerSortDirection, setCustomerSortDirection] = useState<SortDirection>('asc');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const result = await apiClient.getData();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleStartWorkflow = async () => {
    try {
      setStarting(true);
      const result = await apiClient.startWorkflow(autoApprove);
      onWorkflowStarted(result.workflow_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start workflow');
    } finally {
      setStarting(false);
    }
  };

  const toggleTicketExpansion = (ticketId: string) => {
    const newExpanded = new Set(expandedTickets);
    if (newExpanded.has(ticketId)) {
      newExpanded.delete(ticketId);
    } else {
      newExpanded.add(ticketId);
    }
    setExpandedTickets(newExpanded);
  };

  const toggleCustomerExpansion = (customerId: string) => {
    const newExpanded = new Set(expandedCustomers);
    if (newExpanded.has(customerId)) {
      newExpanded.delete(customerId);
    } else {
      newExpanded.add(customerId);
    }
    setExpandedCustomers(newExpanded);
  };

  const formatAssignedTo = (assignedTo: string | null) => {
    if (!assignedTo) return 'Unassigned';
    
    // Format: agent_sarah_tech -> Sarah, Tech
    const parts = assignedTo.replace('agent_', '').split('_');
    if (parts.length >= 2) {
      const name = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
      const dept = parts[1].charAt(0).toUpperCase() + parts[1].slice(1);
      return `${name}, ${dept}`;
    }
    return assignedTo;
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortedTickets = () => {
    if (!data?.tickets) return [];
    
    const tickets = [...data.tickets];
    tickets.sort((a: any, b: any) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      // Handle assigned_to specially
      if (sortField === 'assigned_to') {
        aVal = formatAssignedTo(aVal);
        bVal = formatAssignedTo(bVal);
      }
      
      // Handle support_tier specially
      if (sortField === 'support_tier') {
        aVal = getSupportTier(a.customer_id);
        bVal = getSupportTier(b.customer_id);
      }
      
      // Handle null/undefined
      if (!aVal) return sortDirection === 'asc' ? 1 : -1;
      if (!bVal) return sortDirection === 'asc' ? -1 : 1;
      
      // Priority ordering
      if (sortField === 'priority') {
        const priorityOrder: { [key: string]: number } = {
          critical: 0,
          high: 1,
          medium: 2,
          low: 3
        };
        const aOrder = priorityOrder[aVal.toLowerCase()] ?? 999;
        const bOrder = priorityOrder[bVal.toLowerCase()] ?? 999;
        return sortDirection === 'asc' ? aOrder - bOrder : bOrder - aOrder;
      }
      
      // String comparison
      const comparison = String(aVal).localeCompare(String(bVal));
      return sortDirection === 'asc' ? comparison : -comparison;
    });
    
    return tickets;
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '⇅';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const handleCustomerSort = (field: CustomerSortField) => {
    if (customerSortField === field) {
      // Toggle direction if same field
      setCustomerSortDirection(customerSortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setCustomerSortField(field);
      setCustomerSortDirection('asc');
    }
  };

  const getCustomerSortIcon = (field: CustomerSortField) => {
    if (customerSortField !== field) return '⇅';
    return customerSortDirection === 'asc' ? '↑' : '↓';
  };

  const getSortedCustomers = () => {
    if (!data?.customers) return [];
    
    const customers = [...data.customers];
    customers.sort((a: any, b: any) => {
      let aVal = a[customerSortField];
      let bVal = b[customerSortField];
      
      // Handle null/undefined
      if (!aVal && aVal !== 0) return customerSortDirection === 'asc' ? 1 : -1;
      if (!bVal && bVal !== 0) return customerSortDirection === 'asc' ? -1 : 1;
      
      // Health score ordering (green > yellow > red)
      if (customerSortField === 'health_score') {
        const healthOrder: { [key: string]: number } = {
          green: 0,
          yellow: 1,
          red: 2
        };
        const aOrder = healthOrder[aVal.toLowerCase()] ?? 999;
        const bOrder = healthOrder[bVal.toLowerCase()] ?? 999;
        return customerSortDirection === 'asc' ? aOrder - bOrder : bOrder - aOrder;
      }
      
      // Numeric comparison for satisfaction_score
      if (customerSortField === 'satisfaction_score') {
        const aNum = parseFloat(aVal) || 0;
        const bNum = parseFloat(bVal) || 0;
        return customerSortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }
      
      // String comparison
      const comparison = String(aVal).localeCompare(String(bVal));
      return customerSortDirection === 'asc' ? comparison : -comparison;
    });
    
    return customers;
  };

  const renderStarRating = (score: number | null) => {
    if (!score) return <span className="star-rating-na">N/A</span>;
    
    const stars = [];
    const fullStars = Math.floor(score);
    const hasHalfStar = score % 1 >= 0.5;
    
    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(<span key={i} className="star star-full">★</span>);
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(<span key={i} className="star star-half">★</span>);
      } else {
        stars.push(<span key={i} className="star star-empty">☆</span>);
      }
    }
    
    return (
      <span className="star-rating" title={`${score} out of 5`}>
        {stars}
        <span className="star-rating-value">({score})</span>
      </span>
    );
  };

  const getCompanyName = (customerId: string) => {
    const customer = data?.customers?.find((c: any) => c.customer_id === customerId);
    return customer?.company || customerId;
  };

  const getSupportTier = (customerId: string) => {
    const customer = data?.customers?.find((c: any) => c.customer_id === customerId);
    return customer?.support_tier || 'N/A';
  };

  const getTierClassName = (tierValue: string) => {
    // Extract just the tier name, removing numbers and special characters
    // Examples: "1-premium" -> "premium", "2. priority" -> "priority"
    const cleanTier = tierValue
      .toLowerCase()
      .replace(/^[\d\s\-\.]+/, '') // Remove leading numbers, spaces, dashes, dots
      .replace(/[\d\s\-\.]+$/, '') // Remove trailing numbers, spaces, dashes, dots
      .trim();
    return cleanTier || 'n/a';
  };

  const isTicketModifiedByDAPERL = (ticket: any) => {
    // Check if ticket has been modified by DAPERL workflow
    // DAPERL adds notes with "added_by": "daper_system"
    if (ticket.notes && Array.isArray(ticket.notes)) {
      return ticket.notes.some((note: any) => note.added_by === "daper_system");
    }
    return false;
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading customer support data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={loadData} className="btn-primary">Retry</button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="data-overview">
      <div className="overview-header">
        <h2>📊 Customer Support Data Overview</h2>
        <p className="subtitle">Review the data before starting the DAPERL workflow</p>
      </div>

      {/* Quick Stats */}
      <div className="stats-cards">
        <div className="stat-card-overview tickets">
          <div className="stat-icon">🎫</div>
          <div className="stat-content">
            <div className="stat-value">{data.tickets?.length || 0}</div>
            <div className="stat-label">Support Tickets</div>
          </div>
        </div>
        <div className="stat-card-overview customers">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{data.customers?.length || 0}</div>
            <div className="stat-label">Customers</div>
          </div>
        </div>
        <div className="stat-card-overview products">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <div className="stat-value">{data.product_data?.length || 0}</div>
            <div className="stat-label">Products</div>
          </div>
        </div>
        <div className="stat-card-overview kb">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <div className="stat-value">{data.knowledge_base?.length || 0}</div>
            <div className="stat-label">KB Articles</div>
          </div>
        </div>
      </div>

      {/* Tickets Section */}
      <div className="data-section">
        <h3>🎫 Support Tickets</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleSort('ticket_id')}>
                  ID {getSortIcon('ticket_id')}
                </th>
                <th className="sortable" onClick={() => handleSort('subject')}>
                  Subject {getSortIcon('subject')}
                </th>
                <th className="sortable" onClick={() => handleSort('customer_id')}>
                  Company {getSortIcon('customer_id')}
                </th>
                <th className="sortable" onClick={() => handleSort('support_tier')}>
                  Support Tier {getSortIcon('support_tier')}
                </th>
                <th className="sortable" onClick={() => handleSort('assigned_to')}>
                  Assigned To {getSortIcon('assigned_to')}
                </th>
                <th className="sortable" onClick={() => handleSort('priority')}>
                  Priority {getSortIcon('priority')}
                </th>
                <th className="sortable" onClick={() => handleSort('status')}>
                  Status {getSortIcon('status')}
                </th>
                <th className="sortable" onClick={() => handleSort('category')}>
                  Category {getSortIcon('category')}
                </th>
              </tr>
            </thead>
            <tbody>
              {getSortedTickets().map((ticket: any) => {
                const isExpanded = expandedTickets.has(ticket.ticket_id);
                return (
                  <>
                    <tr 
                      key={ticket.ticket_id}
                      className="clickable-row"
                      onClick={() => toggleTicketExpansion(ticket.ticket_id)}
                    >
                      <td className="ticket-id">
                        {ticket.ticket_id}
                        {isTicketModifiedByDAPERL(ticket) && (
                          <span className="daperl-indicator" title="Modified by DAPERL workflow"> 🤖</span>
                        )}
                      </td>
                      <td className="ticket-subject">
                        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                        {ticket.subject}
                      </td>
                      <td>{getCompanyName(ticket.customer_id)}</td>
                      <td>
                        <span className={`support-tier-badge tier-${getTierClassName(getSupportTier(ticket.customer_id))}`}>
                          {getSupportTier(ticket.customer_id)}
                        </span>
                      </td>
                      <td className="assigned-to">{formatAssignedTo(ticket.assigned_to)}</td>
                      <td>
                        <span className={`priority-badge priority-${ticket.priority}`}>
                          {ticket.priority}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge-small status-${ticket.status}`}>
                          {ticket.status}
                        </span>
                      </td>
                      <td>{ticket.category}</td>
                    </tr>
                    {isExpanded && (
                      <tr key={`${ticket.ticket_id}-details`} className="expanded-row">
                        <td colSpan={8}>
                          <div className="ticket-description">
                            <strong>Description:</strong>
                            <p>{ticket.description}</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Customers Section */}
      <div className="data-section">
        <h3>👥 Customers</h3>
        <div className="table-container">
          <table className="data-table customer-table">
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleCustomerSort('company')}>
                  Company {getCustomerSortIcon('company')}
                </th>
                <th className="sortable" onClick={() => handleCustomerSort('customer_id')}>
                  Customer ID {getCustomerSortIcon('customer_id')}
                </th>
                <th className="sortable" onClick={() => handleCustomerSort('plan')}>
                  Plan {getCustomerSortIcon('plan')}
                </th>
                <th className="sortable" onClick={() => handleCustomerSort('satisfaction_score')}>
                  Satisfaction {getCustomerSortIcon('satisfaction_score')}
                </th>
                <th className="sortable" onClick={() => handleCustomerSort('health_score')}>
                  Health {getCustomerSortIcon('health_score')}
                </th>
              </tr>
            </thead>
            <tbody>
              {getSortedCustomers().map((customer: any) => {
                const isExpanded = expandedCustomers.has(customer.customer_id);
                return (
                  <>
                    <tr 
                      key={customer.customer_id}
                      className={`clickable-row customer-row-${customer.health_score}`}
                      onClick={() => toggleCustomerExpansion(customer.customer_id)}
                    >
                      <td className="customer-company">
                        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                        {customer.company}
                      </td>
                      <td className="customer-id-value">{customer.customer_id}</td>
                      <td>
                        <span className="plan-badge">{customer.plan}</span>
                      </td>
                      <td className="satisfaction-cell">
                        {renderStarRating(customer.satisfaction_score)}
                      </td>
                      <td>
                        <span className={`health-badge health-${customer.health_score}`}>
                          {customer.health_score}
                        </span>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`${customer.customer_id}-details`} className="customer-expanded-row">
                        <td colSpan={5}>
                          <div className="customer-details-grid">
                            <div className="detail-item">
                              <span className="detail-label">Contact:</span>
                              <span>{customer.name}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Email:</span>
                              <a href={`mailto:${customer.email}`} className="contact-email">
                                {customer.email}
                              </a>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Preferred Contact:</span>
                              <span className="contact-method">{customer.preferred_contact}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Support Tier:</span>
                              <span className={`support-tier-badge tier-${getTierClassName(customer.support_tier)}`}>
                                {customer.support_tier}
                              </span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Account Type:</span>
                              <span>{customer.account_type}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Account Value:</span>
                              <span>${customer.account_value?.toLocaleString()}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Company Size:</span>
                              <span>{customer.company_size}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Industry:</span>
                              <span>{customer.industry}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Timezone:</span>
                              <span>{customer.timezone}</span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Total Tickets:</span>
                              <span>{customer.total_tickets}</span>
                            </div>
                            {customer.notes && (
                              <div className="detail-item detail-item-full">
                                <span className="detail-label">Notes:</span>
                                <span>{customer.notes}</span>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Products Section */}
      <div className="data-section">
        <h3 
          className="collapsible-section-header"
          onClick={() => setProductsExpanded(!productsExpanded)}
        >
          <span className="expand-icon">{productsExpanded ? '▼' : '▶'}</span>
          📦 Products & Plans
          <span className="section-count">({data.product_data?.length || 0})</span>
        </h3>
        {productsExpanded && (
          <div className="cards-grid">
            {data.product_data?.map((product: any) => (
              <div key={product.product_id} className="product-card">
                <h4>{product.name}</h4>
                <p className="product-description">{product.description}</p>
                {product.price_monthly && (
                  <div className="product-price">
                    ${product.price_monthly}/mo
                  </div>
                )}
                {product.features && (
                  <ul className="product-features">
                    {product.features.slice(0, 3).map((feature: string, idx: number) => (
                      <li key={idx}>✓ {feature}</li>
                    ))}
                    {product.features.length > 3 && (
                      <li className="more-features">+ {product.features.length - 3} more</li>
                    )}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Workflow Launcher */}
      <div className="workflow-launcher">
        <div className="launcher-content">
          <h3>🚀 Start DAPERL Workflow</h3>
          <p>Analyze this data through the DAPERL framework: Detection, Analysis, Planning, Execution, Reporting, and Learning</p>
          
          <div className="launcher-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={autoApprove}
                onChange={(e) => setAutoApprove(e.target.checked)}
              />
              <span>Auto-approve actions (skip manual approval)</span>
            </label>
          </div>

          <button
            onClick={handleStartWorkflow}
            disabled={starting}
            className="btn-start-workflow"
          >
            {starting ? '🔄 Starting Workflow...' : '🚀 Start Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataOverview;
