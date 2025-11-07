"""
Customer Support tools for the DAPER framework.
Implements tools for ticket management, customer account updates, 
knowledge base operations, and notifications.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools import BaseTool, ToolRegistry, ToolInfo


class UpdateTicketStatusTool(BaseTool):
    """Tool for updating ticket status and adding notes."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update ticket status and add internal notes."""
        ticket_id = arguments.get("ticket_id")
        new_status = arguments.get("status")
        notes = arguments.get("notes", "")
        assigned_to = arguments.get("assigned_to")
        
        if not ticket_id or not new_status:
            return self.create_response(
                success=False,
                data={"error": "ticket_id and status are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would update the ticketing system
        update_result = {
            "ticket_id": ticket_id,
            "previous_status": "open",  # Would be fetched from system
            "new_status": new_status,
            "notes_added": notes,
            "assigned_to": assigned_to,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "daper_system"
        }
        
        self.logger.info(f"Updated ticket {ticket_id} to status: {new_status}")
        
        return self.create_response(
            success=True,
            data=update_result,
            additional_notes=f"Successfully updated ticket {ticket_id}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="update_ticket_status",
            description="Update ticket status and add internal notes",
            parameters=["ticket_id", "status", "notes", "assigned_to"],
            domain=self.domain,
            tool_class=UpdateTicketStatusTool
        )


class SendCustomerResponseTool(BaseTool):
    """Tool for sending responses to customers."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Send a response to a customer."""
        ticket_id = arguments.get("ticket_id")
        customer_id = arguments.get("customer_id")
        response_text = arguments.get("response_text")
        response_type = arguments.get("response_type", "email")  # email, phone, chat
        template_id = arguments.get("template_id")
        
        if not all([ticket_id, customer_id, response_text]):
            return self.create_response(
                success=False,
                data={"error": "ticket_id, customer_id, and response_text are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would integrate with email/chat systems
        response_result = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "response_id": f"RESP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "response_type": response_type,
            "template_used": template_id,
            "sent_at": datetime.utcnow().isoformat(),
            "delivery_status": "sent",
            "response_length": len(response_text)
        }
        
        self.logger.info(f"Sent {response_type} response to customer {customer_id} for ticket {ticket_id}")
        
        return self.create_response(
            success=True,
            data=response_result,
            additional_notes=f"Response sent successfully via {response_type}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="send_customer_response",
            description="Send response to customer via email, phone, or chat",
            parameters=["ticket_id", "customer_id", "response_text", "response_type", "template_id"],
            domain=self.domain,
            tool_class=SendCustomerResponseTool
        )


class UpdateCustomerAccountTool(BaseTool):
    """Tool for updating customer account settings and preferences."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer account information."""
        customer_id = arguments.get("customer_id")
        updates = arguments.get("updates", {})
        reason = arguments.get("reason", "Support request")
        
        if not customer_id or not updates:
            return self.create_response(
                success=False,
                data={"error": "customer_id and updates are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would update the CRM/customer database
        valid_fields = [
            "account_type", "plan", "support_tier", "preferred_contact",
            "health_score", "notes"
        ]
        
        applied_updates = {}
        for field, value in updates.items():
            if field in valid_fields:
                applied_updates[field] = value
        
        update_result = {
            "customer_id": customer_id,
            "updates_applied": applied_updates,
            "reason": reason,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "daper_system"
        }
        
        self.logger.info(f"Updated customer {customer_id} account: {list(applied_updates.keys())}")
        
        return self.create_response(
            success=True,
            data=update_result,
            additional_notes=f"Updated {len(applied_updates)} fields for customer {customer_id}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="update_customer_account",
            description="Update customer account settings and preferences",
            parameters=["customer_id", "updates", "reason"],
            domain=self.domain,
            tool_class=UpdateCustomerAccountTool
        )


class SearchKnowledgeBaseTool(BaseTool):
    """Tool for searching knowledge base articles."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search knowledge base for relevant articles."""
        query = arguments.get("query")
        category = arguments.get("category")
        max_results = arguments.get("max_results", 5)
        
        if not query:
            return self.create_response(
                success=False,
                data={"error": "query is required"},
                additional_notes="Search query parameter is missing"
            )
        
        # Mock implementation - in real usage, this would search the actual knowledge base
        mock_results = self._generate_mock_search_results(query, category, max_results)
        
        search_result = {
            "query": query,
            "category_filter": category,
            "results_count": len(mock_results),
            "max_results": max_results,
            "articles": mock_results,
            "searched_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Knowledge base search for '{query}' returned {len(mock_results)} results")
        
        return self.create_response(
            success=True,
            data=search_result,
            additional_notes=f"Found {len(mock_results)} relevant articles"
        )
    
    def _generate_mock_search_results(self, query: str, category: Optional[str], max_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results based on query."""
        # Mock knowledge base articles
        mock_kb = [
            {
                "article_id": "KB-001",
                "title": "Setting up SAML Single Sign-On (SSO)",
                "category": "authentication",
                "relevance_score": 0.95 if "sso" in query.lower() or "saml" in query.lower() else 0.1,
                "url": "/kb/sso-setup",
                "summary": "Complete guide for setting up SAML SSO for Enterprise accounts"
            },
            {
                "article_id": "KB-002", 
                "title": "Understanding API Rate Limits",
                "category": "development",
                "relevance_score": 0.98 if "api" in query.lower() or "rate limit" in query.lower() else 0.1,
                "url": "/kb/api-limits",
                "summary": "Comprehensive guide to API rate limits across all plans"
            },
            {
                "article_id": "KB-003",
                "title": "Analytics Addon: Features and Data Update Frequencies", 
                "category": "analytics",
                "relevance_score": 0.92 if "analytics" in query.lower() or "real-time" in query.lower() else 0.1,
                "url": "/kb/analytics-addon",
                "summary": "Details about Analytics addon features and data refresh rates"
            },
            {
                "article_id": "KB-004",
                "title": "Account Security: Lockouts and Recovery",
                "category": "security", 
                "relevance_score": 0.89 if "lockout" in query.lower() or "security" in query.lower() else 0.1,
                "url": "/kb/account-security",
                "summary": "How to recover from account lockouts and security best practices"
            },
            {
                "article_id": "KB-005",
                "title": "Refund Policy and Process",
                "category": "billing",
                "relevance_score": 0.96 if "refund" in query.lower() or "billing" in query.lower() else 0.1,
                "url": "/kb/refund-policy",
                "summary": "Complete refund policy and step-by-step process"
            }
        ]
        
        # Filter by category if specified
        if category:
            mock_kb = [article for article in mock_kb if article["category"] == category]
        
        # Sort by relevance and limit results
        mock_kb.sort(key=lambda x: x["relevance_score"], reverse=True)
        relevant_articles = [article for article in mock_kb if article["relevance_score"] > 0.5]
        
        return relevant_articles[:max_results]
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="search_knowledge_base",
            description="Search knowledge base articles for customer issues",
            parameters=["query", "category", "max_results"],
            domain=self.domain,
            tool_class=SearchKnowledgeBaseTool
        )


class EscalateToSpecialistTool(BaseTool):
    """Tool for escalating tickets to appropriate specialists."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate ticket to appropriate specialist team."""
        ticket_id = arguments.get("ticket_id")
        specialist_type = arguments.get("specialist_type")
        urgency = arguments.get("urgency", "normal")
        context = arguments.get("context", "")
        
        if not ticket_id or not specialist_type:
            return self.create_response(
                success=False,
                data={"error": "ticket_id and specialist_type are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would route to appropriate teams
        specialist_mapping = {
            "technical_support": "Tech Support Team",
            "billing_specialist": "Billing Department", 
            "security_specialist": "Security Team",
            "enterprise_specialist": "Enterprise Success Team",
            "escalation_manager": "Support Manager"
        }
        
        team_name = specialist_mapping.get(specialist_type, "General Support")
        
        escalation_result = {
            "ticket_id": ticket_id,
            "specialist_type": specialist_type,
            "escalated_to_team": team_name,
            "urgency": urgency,
            "context_provided": context,
            "escalated_at": datetime.utcnow().isoformat(),
            "escalation_id": f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "expected_response_time": self._get_specialist_response_time(specialist_type, urgency)
        }
        
        self.logger.info(f"Escalated ticket {ticket_id} to {team_name} with {urgency} urgency")
        
        return self.create_response(
            success=True,
            data=escalation_result,
            additional_notes=f"Successfully escalated to {team_name}"
        )
    
    def _get_specialist_response_time(self, specialist_type: str, urgency: str) -> str:
        """Get expected response time based on specialist and urgency."""
        base_times = {
            "technical_support": "2-4 hours",
            "billing_specialist": "1-2 hours", 
            "security_specialist": "30 minutes - 1 hour",
            "enterprise_specialist": "1-2 hours",
            "escalation_manager": "15-30 minutes"
        }
        
        base_time = base_times.get(specialist_type, "2-4 hours")
        
        if urgency == "critical":
            return f"URGENT: {base_time} (expedited)"
        elif urgency == "high":
            return base_time
        else:
            return f"{base_time} (normal queue)"
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="escalate_to_specialist",
            description="Escalate ticket to appropriate specialist team",
            parameters=["ticket_id", "specialist_type", "urgency", "context"],
            domain=self.domain,
            tool_class=EscalateToSpecialistTool
        )


class NotifyAccountManagerTool(BaseTool):
    """Tool for notifying account managers about customer issues."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Notify account manager about customer situation."""
        customer_id = arguments.get("customer_id")
        issue_summary = arguments.get("issue_summary")
        urgency = arguments.get("urgency", "normal")
        recommended_action = arguments.get("recommended_action")
        
        if not all([customer_id, issue_summary]):
            return self.create_response(
                success=False,
                data={"error": "customer_id and issue_summary are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would notify via Slack, email, etc.
        notification_result = {
            "customer_id": customer_id,
            "issue_summary": issue_summary,
            "urgency": urgency,
            "recommended_action": recommended_action,
            "notified_at": datetime.utcnow().isoformat(),
            "notification_id": f"AM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "account_manager": self._get_account_manager(customer_id),
            "delivery_method": "slack_and_email"
        }
        
        self.logger.info(f"Notified account manager about customer {customer_id} issue")
        
        return self.create_response(
            success=True,
            data=notification_result,
            additional_notes="Account manager notification sent"
        )
    
    def _get_account_manager(self, customer_id: str) -> str:
        """Get account manager for customer (mock implementation)."""
        # Mock assignment based on customer ID
        if "12345" in customer_id:
            return "Sarah Johnson"
        elif "67890" in customer_id:
            return "Michael Chen"  
        elif "11111" in customer_id:
            return "Emily Rodriguez"
        else:
            return "General Account Team"
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="notify_account_manager",
            description="Notify account manager about customer issues",
            parameters=["customer_id", "issue_summary", "urgency", "recommended_action"],
            domain=self.domain,
            tool_class=NotifyAccountManagerTool
        )


class CreateFollowUpTaskTool(BaseTool):
    """Tool for creating follow-up tasks and reminders."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a follow-up task or reminder."""
        ticket_id = arguments.get("ticket_id")
        task_description = arguments.get("task_description") 
        assigned_to = arguments.get("assigned_to")
        due_date = arguments.get("due_date")
        task_type = arguments.get("task_type", "follow_up")
        
        if not all([ticket_id, task_description]):
            return self.create_response(
                success=False,
                data={"error": "ticket_id and task_description are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage, this would create tasks in project management system
        task_result = {
            "task_id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "ticket_id": ticket_id,
            "task_description": task_description,
            "task_type": task_type,
            "assigned_to": assigned_to or "support_team",
            "due_date": due_date or self._calculate_default_due_date(task_type),
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
            "priority": "normal"
        }
        
        self.logger.info(f"Created {task_type} task for ticket {ticket_id}")
        
        return self.create_response(
            success=True,
            data=task_result,
            additional_notes=f"Follow-up task created successfully"
        )
    
    def _calculate_default_due_date(self, task_type: str) -> str:
        """Calculate default due date based on task type."""
        from datetime import timedelta
        
        days_mapping = {
            "follow_up": 3,
            "check_in": 7,
            "satisfaction_survey": 5,
            "account_review": 14
        }
        
        days = days_mapping.get(task_type, 3)
        due_date = datetime.now() + timedelta(days=days)
        return due_date.isoformat()
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="create_follow_up_task",
            description="Create follow-up tasks and reminders for tickets",
            parameters=["ticket_id", "task_description", "assigned_to", "due_date", "task_type"],
            domain=self.domain,
            tool_class=CreateFollowUpTaskTool
        )


def register_customer_support_tools(domain: str = "customer_support"):
    """Register customer support tools for a domain."""
    print(f"Registering customer support tools for domain: {domain}")
    
    tools = [
        UpdateTicketStatusTool,
        SendCustomerResponseTool, 
        UpdateCustomerAccountTool,
        SearchKnowledgeBaseTool,
        EscalateToSpecialistTool,
        NotifyAccountManagerTool,
        CreateFollowUpTaskTool
    ]
    
    for tool_class in tools:
        ToolRegistry.register_tool(tool_class, domain)
        print(f"  ✅ Registered: {tool_class.__name__}")
    
    print(f"Customer support tools registered successfully for {domain}!")


if __name__ == "__main__":
    # Register customer support tools
    register_customer_support_tools()
    
    # List registered tools
    print("\nRegistered Customer Support Tools:")
    for tool in ToolRegistry.get_tools_for_domain("customer_support"):
        print(f"  - {tool['name']}: {tool['description']}")