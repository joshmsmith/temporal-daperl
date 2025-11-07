"""
Customer Support domain implementation for the DAPER framework.
Demonstrates intelligent ticket routing, customer sentiment analysis, 
and automated support workflows with multi-source data integration.
"""

import sys
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.activities.base import DetectActivity, AnalyzeActivity, PlanActivity
from src.tools import BaseTool, ToolRegistry, ToolInfo
from src.data_loaders import BaseDataLoader, DataLoaderRegistry, DataLoaderInfo


class CustomerSupportDetectActivity(DetectActivity):
    """
    Customer support detection activity.
    Identifies urgent tickets, escalation patterns, and customer satisfaction issues.
    """
    
    async def detect(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect customer support issues requiring attention."""
        self.validate_input(input_data)
        self.heartbeat("Starting customer support detection...")
        
        # Load customer support data from all sources
        support_data = await self._load_support_data(input_data.get("data_sources", []))
        
        if not support_data:
            return self.create_response(
                success=False,
                data={"error": "No customer support data loaded"},
                additional_notes="Detection requires customer support data sources"
            )
        
        # Detect various types of issues
        issues = []
        
        # Detect urgent tickets
        urgent_issues = self._detect_urgent_tickets(support_data.get("tickets", []))
        issues.extend(urgent_issues)
        
        # Detect customer satisfaction issues
        satisfaction_issues = self._detect_satisfaction_issues(
            support_data.get("customers", []), 
            support_data.get("tickets", [])
        )
        issues.extend(satisfaction_issues)
        
        # Detect escalation patterns
        escalation_issues = self._detect_escalation_patterns(
            support_data.get("tickets", []),
            support_data.get("community_forums", [])
        )
        issues.extend(escalation_issues)
        
        # Detect knowledge gaps
        knowledge_issues = self._detect_knowledge_gaps(
            support_data.get("tickets", []),
            support_data.get("knowledge_base", []),
            support_data.get("community_forums", [])
        )
        issues.extend(knowledge_issues)
        
        return self.create_response(
            success=True,
            data={
                "issues": issues,
                "total_issues": len(issues),
                "detection_method": "customer_support_multi_source",
                "data_sources_processed": len(input_data.get("data_sources", [])),
                "summary": self._generate_detection_summary(issues)
            },
            confidence_score=0.95,
            additional_notes=f"Detected {len(issues)} customer support issues across multiple categories"
        )
    
    async def _load_support_data(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Load data from all customer support sources."""
        combined_data = {}
        
        for source in data_sources:
            loader = self._get_data_loader(source["name"])
            if loader:
                result = await loader.load_data(source["config"])
                if result.get("success"):
                    # Merge data based on source type
                    source_data = result["data"]
                    if "customer_support_data" in source_data:
                        support_data = source_data["customer_support_data"]
                        for key, value in support_data.items():
                            if key == "metadata":
                                continue
                            if key in combined_data:
                                if isinstance(value, list):
                                    combined_data[key].extend(value)
                                else:
                                    combined_data[key] = value
                            else:
                                combined_data[key] = value
        
        return combined_data
    
    def _detect_urgent_tickets(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect tickets requiring urgent attention."""
        urgent_issues = []
        
        for ticket in tickets:
            # Check for SLA violations
            if self._is_sla_violation(ticket):
                urgent_issues.append({
                    "issue_id": f"sla_violation_{ticket['ticket_id']}",
                    "type": "sla_violation",
                    "description": f"Ticket {ticket['ticket_id']} is approaching or has exceeded SLA",
                    "severity": "critical" if self._is_sla_exceeded(ticket) else "high",
                    "affected_components": [ticket["ticket_id"]],
                    "customer_id": ticket["customer_id"],
                    "urgency": "immediate" if self._is_sla_exceeded(ticket) else "within_hour",
                    "source_data": ticket
                })
            
            # Check for high-priority unassigned tickets
            if (ticket.get("priority") in ["critical", "high"] and 
                not ticket.get("assigned_to") and 
                ticket.get("status") == "open"):
                urgent_issues.append({
                    "issue_id": f"unassigned_priority_{ticket['ticket_id']}",
                    "type": "unassigned_priority_ticket",
                    "description": f"High-priority ticket {ticket['ticket_id']} is unassigned",
                    "severity": "high",
                    "affected_components": [ticket["ticket_id"]],
                    "customer_id": ticket["customer_id"],
                    "urgency": "within_hour",
                    "source_data": ticket
                })
            
            # Check for negative customer sentiment
            if ticket.get("customer_sentiment") in ["frustrated", "angry", "disappointed"]:
                urgent_issues.append({
                    "issue_id": f"negative_sentiment_{ticket['ticket_id']}",
                    "type": "customer_sentiment_issue",
                    "description": f"Customer shows {ticket['customer_sentiment']} sentiment in ticket {ticket['ticket_id']}",
                    "severity": "medium",
                    "affected_components": [ticket["ticket_id"]],
                    "customer_id": ticket["customer_id"],
                    "urgency": "within_4_hours",
                    "source_data": ticket
                })
        
        return urgent_issues
    
    def _detect_satisfaction_issues(self, customers: List[Dict[str, Any]], tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect customer satisfaction and churn risk issues."""
        satisfaction_issues = []
        
        for customer in customers:
            customer_id = customer["customer_id"]
            
            # Low satisfaction score
            satisfaction_score = customer.get("satisfaction_score")
            if satisfaction_score is not None and satisfaction_score < 3.5:
                satisfaction_issues.append({
                    "issue_id": f"low_satisfaction_{customer_id}",
                    "type": "low_customer_satisfaction",
                    "description": f"Customer {customer['name']} has low satisfaction score: {satisfaction_score}/5",
                    "severity": "medium",
                    "affected_components": [customer_id],
                    "customer_id": customer_id,
                    "urgency": "within_24_hours",
                    "source_data": customer
                })
            
            # Health score issues
            if customer.get("health_score") == "red":
                satisfaction_issues.append({
                    "issue_id": f"churn_risk_{customer_id}",
                    "type": "customer_churn_risk",
                    "description": f"Customer {customer['name']} shows high churn risk (red health score)",
                    "severity": "high",
                    "affected_components": [customer_id],
                    "customer_id": customer_id,
                    "urgency": "within_4_hours",
                    "source_data": customer
                })
            
            # Recent plan downgrades
            if (customer.get("previous_plan") and 
                self._is_plan_downgrade(customer.get("previous_plan"), customer.get("plan"))):
                satisfaction_issues.append({
                    "issue_id": f"plan_downgrade_{customer_id}",
                    "type": "plan_downgrade_follow_up",
                    "description": f"Customer {customer['name']} downgraded from {customer['previous_plan']} to {customer['plan']}",
                    "severity": "medium",
                    "affected_components": [customer_id],
                    "customer_id": customer_id,
                    "urgency": "within_24_hours",
                    "source_data": customer
                })
        
        return satisfaction_issues
    
    def _detect_escalation_patterns(self, tickets: List[Dict[str, Any]], forums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns indicating escalation needs."""
        escalation_issues = []
        
        # Group tickets by customer to detect patterns
        customer_tickets = {}
        for ticket in tickets:
            customer_id = ticket["customer_id"]
            if customer_id not in customer_tickets:
                customer_tickets[customer_id] = []
            customer_tickets[customer_id].append(ticket)
        
        # Detect customers with multiple recent tickets
        for customer_id, customer_ticket_list in customer_tickets.items():
            recent_tickets = [t for t in customer_ticket_list 
                            if self._is_recent_ticket(t, days=7)]
            
            if len(recent_tickets) >= 2:
                escalation_issues.append({
                    "issue_id": f"multiple_tickets_{customer_id}",
                    "type": "customer_escalation_pattern",
                    "description": f"Customer {customer_id} has {len(recent_tickets)} tickets in the past week",
                    "severity": "medium",
                    "affected_components": [customer_id],
                    "customer_id": customer_id,
                    "urgency": "within_8_hours",
                    "source_data": {"tickets": recent_tickets}
                })
        
        # Detect forum posts from customers with open tickets
        ticket_customer_ids = {t["customer_id"] for t in tickets if t["status"] in ["open", "in_progress"]}
        
        for forum_post in forums:
            if (forum_post.get("customer_id") in ticket_customer_ids and
                forum_post.get("status") == "active"):
                escalation_issues.append({
                    "issue_id": f"forum_escalation_{forum_post['post_id']}",
                    "type": "forum_ticket_escalation",
                    "description": f"Customer with open ticket posted in forum: {forum_post['title']}",
                    "severity": "medium",
                    "affected_components": [forum_post["customer_id"]],
                    "customer_id": forum_post["customer_id"],
                    "urgency": "within_4_hours",
                    "source_data": forum_post
                })
        
        return escalation_issues
    
    def _detect_knowledge_gaps(self, tickets: List[Dict[str, Any]], 
                              knowledge_base: List[Dict[str, Any]],
                              forums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect knowledge base gaps and common issues."""
        knowledge_issues = []
        
        # Analyze common ticket categories without knowledge base coverage
        ticket_categories = {}
        for ticket in tickets:
            category = f"{ticket.get('category', 'unknown')}_{ticket.get('subcategory', 'general')}"
            if category not in ticket_categories:
                ticket_categories[category] = []
            ticket_categories[category].append(ticket)
        
        # Check which categories have multiple tickets but limited knowledge base coverage
        kb_categories = {f"{kb.get('category', 'unknown')}_{kb.get('subcategory', 'general')}" 
                        for kb in knowledge_base}
        
        for category, category_tickets in ticket_categories.items():
            if len(category_tickets) >= 2 and category not in kb_categories:
                knowledge_issues.append({
                    "issue_id": f"knowledge_gap_{category}",
                    "type": "knowledge_base_gap",
                    "description": f"Multiple tickets in category '{category}' but no knowledge base article",
                    "severity": "low",
                    "affected_components": ["knowledge_base"],
                    "urgency": "within_week",
                    "source_data": {
                        "category": category,
                        "ticket_count": len(category_tickets),
                        "tickets": category_tickets
                    }
                })
        
        # Detect forum questions that could be answered better with KB articles
        common_forum_topics = {}
        for post in forums:
            if post.get("replies", 0) >= 3:  # Popular questions
                for tag in post.get("tags", []):
                    if tag not in common_forum_topics:
                        common_forum_topics[tag] = []
                    common_forum_topics[tag].append(post)
        
        for topic, posts in common_forum_topics.items():
            if len(posts) >= 2:  # Multiple popular questions on same topic
                knowledge_issues.append({
                    "issue_id": f"forum_knowledge_gap_{topic}",
                    "type": "forum_knowledge_opportunity",
                    "description": f"Popular forum topic '{topic}' with {len(posts)} active discussions",
                    "severity": "low",
                    "affected_components": ["knowledge_base", "community_forums"],
                    "urgency": "within_week",
                    "source_data": {
                        "topic": topic,
                        "post_count": len(posts),
                        "posts": posts
                    }
                })
        
        return knowledge_issues
    
    def _is_sla_violation(self, ticket: Dict[str, Any]) -> bool:
        """Check if ticket is approaching or has exceeded SLA."""
        created_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
        now = datetime.now(created_at.tzinfo)
        age_hours = (now - created_at).total_seconds() / 3600
        
        response_sla_str = ticket.get("response_time_sla", "24 hours")
        response_sla_hours = self._parse_sla_hours(response_sla_str)
        
        # Consider violation if 75% of SLA time has passed and no response
        if ticket.get("status") == "open" and not ticket.get("assigned_to"):
            return age_hours >= (response_sla_hours * 0.75)
        
        return False
    
    def _is_sla_exceeded(self, ticket: Dict[str, Any]) -> bool:
        """Check if ticket has exceeded SLA."""
        created_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
        now = datetime.now(created_at.tzinfo)
        age_hours = (now - created_at).total_seconds() / 3600
        
        response_sla_str = ticket.get("response_time_sla", "24 hours")
        response_sla_hours = self._parse_sla_hours(response_sla_str)
        
        return age_hours > response_sla_hours
    
    def _parse_sla_hours(self, sla_str: str) -> float:
        """Parse SLA string to hours."""
        if "hour" in sla_str:
            return float(re.findall(r'\d+', sla_str)[0])
        elif "day" in sla_str:
            return float(re.findall(r'\d+', sla_str)[0]) * 24
        return 24.0  # Default to 24 hours
    
    def _is_recent_ticket(self, ticket: Dict[str, Any], days: int = 7) -> bool:
        """Check if ticket was created in the last N days."""
        created_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
        cutoff = datetime.now(created_at.tzinfo) - timedelta(days=days)
        return created_at > cutoff
    
    def _is_plan_downgrade(self, previous_plan: str, current_plan: str) -> bool:
        """Check if current plan is a downgrade from previous."""
        plan_hierarchy = ["Basic", "Pro", "Business", "Enterprise"]
        try:
            prev_idx = plan_hierarchy.index(previous_plan.split()[0])
            curr_idx = plan_hierarchy.index(current_plan.split()[0])
            return curr_idx < prev_idx
        except (ValueError, IndexError):
            return False
    
    def _generate_detection_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of detected issues."""
        summary = {
            "total_issues": len(issues),
            "by_severity": {},
            "by_type": {},
            "urgent_actions_needed": 0
        }
        
        for issue in issues:
            # Count by severity
            severity = issue.get("severity", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Count by type
            issue_type = issue.get("type", "unknown")
            summary["by_type"][issue_type] = summary["by_type"].get(issue_type, 0) + 1
            
            # Count urgent actions
            if issue.get("urgency") in ["immediate", "within_hour"]:
                summary["urgent_actions_needed"] += 1
        
        return summary


class CustomerSupportAnalyzeActivity(AnalyzeActivity):
    """
    Customer support analysis activity.
    Provides intelligent analysis of customer context, history, and optimal response strategies.
    """
    
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer support issues with domain expertise."""
        # Get base analysis
        base_result = await super().analyze(input_data)
        
        if not base_result.get("success"):
            return base_result
        
        # Enhance with customer support domain knowledge
        issues = base_result["data"]["issues"]
        enhanced_issues = []
        
        # Load customer and product data for context
        support_data = await self._load_analysis_context(input_data.get("data_sources", []))
        
        for issue in issues:
            enhanced_issue = issue.copy()
            enhancement = self._analyze_customer_support_issue(issue, support_data)
            enhanced_issue.update(enhancement)
            enhanced_issues.append(enhanced_issue)
        
        # Add overall customer support insights
        support_insights = self._generate_support_insights(enhanced_issues, support_data)
        
        base_result["data"].update({
            "issues": enhanced_issues,
            "support_insights": support_insights
        })
        base_result["additional_notes"] += " Enhanced with customer support domain expertise."
        
        return base_result
    
    async def _load_analysis_context(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Load additional context data for analysis."""
        context_data = {"customers": [], "products": [], "knowledge_base": []}
        
        for source in data_sources:
            loader = self._get_data_loader(source["name"])
            if loader:
                result = await loader.load_data(source["config"])
                if result.get("success") and "customer_support_data" in result["data"]:
                    support_data = result["data"]["customer_support_data"]
                    for key in ["customers", "product_data", "knowledge_base"]:
                        if key in support_data:
                            if key == "product_data":
                                context_data["products"].extend(support_data[key])
                            else:
                                context_data[key.replace("_data", "s")].extend(support_data[key])
        
        return context_data
    
    def _analyze_customer_support_issue(self, issue: Dict[str, Any], 
                                       support_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific customer support issue."""
        customer_id = issue.get("customer_id")
        issue_type = issue.get("type", "")
        
        analysis = {
            "customer_context": {},
            "recommended_approach": "",
            "expertise_required": [],
            "escalation_path": "",
            "expected_resolution_time": "",
            "customer_history": {},
            "related_articles": []
        }
        
        # Get customer context
        customer = self._find_customer(customer_id, support_data.get("customers", []))
        if customer:
            analysis["customer_context"] = self._analyze_customer_context(customer)
            analysis["customer_history"] = self._get_customer_history(customer)
        
        # Determine approach based on issue type
        analysis["recommended_approach"] = self._get_recommended_approach(issue_type, customer)
        
        # Determine required expertise
        analysis["expertise_required"] = self._determine_required_expertise(issue_type, customer)
        
        # Determine escalation path
        analysis["escalation_path"] = self._determine_escalation_path(issue, customer)
        
        # Estimate resolution time
        analysis["expected_resolution_time"] = self._estimate_resolution_time(issue_type, customer)
        
        # Find related knowledge base articles
        analysis["related_articles"] = self._find_related_articles(
            issue, support_data.get("knowledge_base", [])
        )
        
        return analysis
    
    def _find_customer(self, customer_id: str, customers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find customer data by ID."""
        for customer in customers:
            if customer.get("customer_id") == customer_id:
                return customer
        return None
    
    def _analyze_customer_context(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer context and characteristics."""
        context = {
            "account_type": customer.get("account_type", "unknown"),
            "account_value": customer.get("account_value", 0),
            "support_tier": customer.get("support_tier", "community"),
            "health_score": customer.get("health_score", "unknown"),
            "satisfaction_score": customer.get("satisfaction_score"),
            "industry": customer.get("industry", "unknown"),
            "company_size": customer.get("company_size", "unknown"),
            "tenure_days": self._calculate_tenure_days(customer.get("signup_date")),
            "risk_factors": self._identify_risk_factors(customer)
        }
        return context
    
    def _get_customer_history(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer history summary."""
        return {
            "total_tickets": customer.get("total_tickets", 0),
            "satisfaction_score": customer.get("satisfaction_score"),
            "recent_plan_changes": self._get_recent_plan_changes(customer),
            "support_interaction_frequency": self._calculate_interaction_frequency(customer),
            "preferred_contact": customer.get("preferred_contact", "email")
        }
    
    def _get_recommended_approach(self, issue_type: str, customer: Optional[Dict[str, Any]]) -> str:
        """Get recommended approach based on issue type and customer."""
        if not customer:
            return "standard_support_process"
        
        account_type = customer.get("account_type", "basic")
        support_tier = customer.get("support_tier", "community")
        health_score = customer.get("health_score", "green")
        
        # High-value customer or churn risk
        if (customer.get("account_value", 0) > 10000 or 
            health_score == "red" or 
            support_tier == "premium"):
            return "white_glove_service"
        
        # Technical issues for business+ customers
        if ("technical" in issue_type or "api" in issue_type) and account_type in ["business", "enterprise"]:
            return "technical_specialist_assignment"
        
        # Billing issues
        if "billing" in issue_type or "refund" in issue_type:
            return "billing_team_priority"
        
        # Security issues
        if "security" in issue_type or "lockout" in issue_type:
            return "security_team_immediate"
        
        # Sentiment-based approach
        if "sentiment" in issue_type:
            return "empathy_focused_response"
        
        return "standard_support_process"
    
    def _determine_required_expertise(self, issue_type: str, customer: Optional[Dict[str, Any]]) -> List[str]:
        """Determine what expertise is required for this issue."""
        expertise = []
        
        if "api" in issue_type or "technical" in issue_type:
            expertise.append("technical_support")
        
        if "billing" in issue_type or "refund" in issue_type:
            expertise.append("billing_specialist")
        
        if "sso" in issue_type or "saml" in issue_type:
            expertise.append("security_specialist")
        
        if "enterprise" in issue_type or (customer and customer.get("account_type") == "enterprise"):
            expertise.append("enterprise_specialist")
        
        if not expertise:
            expertise.append("general_support")
        
        return expertise
    
    def _determine_escalation_path(self, issue: Dict[str, Any], customer: Optional[Dict[str, Any]]) -> str:
        """Determine escalation path for the issue."""
        severity = issue.get("severity", "medium")
        issue_type = issue.get("type", "")
        
        if not customer:
            return "standard_escalation"
        
        account_value = customer.get("account_value", 0)
        support_tier = customer.get("support_tier", "community")
        
        # Critical issues or high-value customers
        if severity == "critical" or account_value > 20000:
            return "immediate_manager_escalation"
        
        # Premium support customers
        if support_tier == "premium":
            return "account_manager_escalation"
        
        # Technical escalation
        if "technical" in issue_type or "api" in issue_type:
            return "technical_lead_escalation"
        
        return "standard_escalation"
    
    def _estimate_resolution_time(self, issue_type: str, customer: Optional[Dict[str, Any]]) -> str:
        """Estimate resolution time based on issue complexity and customer tier."""
        base_times = {
            "account_lockout": "15-30 minutes",
            "billing_issue": "2-4 hours",
            "technical_issue": "4-8 hours",
            "sso_setup": "1-2 days",
            "refund_request": "2-3 days",
            "knowledge_gap": "1 week"
        }
        
        # Map issue types to categories
        for category, time in base_times.items():
            if category.split("_")[0] in issue_type:
                if customer and customer.get("support_tier") == "premium":
                    return f"50% faster: {time}"
                return time
        
        return "4-24 hours"
    
    def _find_related_articles(self, issue: Dict[str, Any], 
                              knowledge_base: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Find knowledge base articles related to the issue."""
        issue_type = issue.get("type", "")
        source_data = issue.get("source_data", {})
        
        related_articles = []
        
        for article in knowledge_base:
            # Check if article tags match issue characteristics
            article_tags = article.get("tags", [])
            article_category = article.get("subcategory", "")
            
            # Direct category match
            if article_category in issue_type:
                related_articles.append({
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "relevance": "high",
                    "match_reason": "direct_category_match"
                })
                continue
            
            # Tag matches
            issue_keywords = self._extract_issue_keywords(issue_type, source_data)
            matching_tags = set(article_tags) & set(issue_keywords)
            
            if matching_tags:
                related_articles.append({
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "relevance": "medium" if len(matching_tags) > 1 else "low",
                    "match_reason": f"tag_match: {', '.join(matching_tags)}"
                })
        
        # Sort by relevance and limit to top 5
        relevance_order = {"high": 3, "medium": 2, "low": 1}
        related_articles.sort(key=lambda x: relevance_order.get(x["relevance"], 0), reverse=True)
        
        return related_articles[:5]
    
    def _calculate_tenure_days(self, signup_date_str: Optional[str]) -> int:
        """Calculate customer tenure in days."""
        if not signup_date_str:
            return 0
        try:
            signup_date = datetime.fromisoformat(signup_date_str.replace("Z", "+00:00"))
            return (datetime.now(signup_date.tzinfo) - signup_date).days
        except:
            return 0
    
    def _identify_risk_factors(self, customer: Dict[str, Any]) -> List[str]:
        """Identify customer churn risk factors."""
        risk_factors = []
        
        if customer.get("health_score") == "red":
            risk_factors.append("red_health_score")
        
        if customer.get("satisfaction_score", 5.0) < 3.5:
            risk_factors.append("low_satisfaction")
        
        if "downgrade" in customer.get("notes", "").lower():
            risk_factors.append("recent_downgrade")
        
        # High ticket volume relative to tenure
        tenure_days = self._calculate_tenure_days(customer.get("signup_date"))
        ticket_rate = customer.get("total_tickets", 0) / max(tenure_days / 30, 1)  # Tickets per month
        if ticket_rate > 3:
            risk_factors.append("high_support_volume")
        
        return risk_factors
    
    def _get_recent_plan_changes(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about recent plan changes."""
        current_plan = customer.get("plan")
        previous_plan = customer.get("previous_plan")
        plan_start_date = customer.get("plan_start_date")
        
        if previous_plan and current_plan != previous_plan:
            is_upgrade = self._is_plan_upgrade(previous_plan, current_plan)
            return {
                "changed": True,
                "from_plan": previous_plan,
                "to_plan": current_plan,
                "change_type": "upgrade" if is_upgrade else "downgrade",
                "change_date": plan_start_date
            }
        
        return {"changed": False}
    
    def _is_plan_upgrade(self, previous_plan: str, current_plan: str) -> bool:
        """Check if current plan is an upgrade from previous."""
        plan_hierarchy = ["Basic", "Pro", "Business", "Enterprise"]
        try:
            prev_idx = plan_hierarchy.index(previous_plan.split()[0])
            curr_idx = plan_hierarchy.index(current_plan.split()[0])
            return curr_idx > prev_idx
        except (ValueError, IndexError):
            return False
    
    def _calculate_interaction_frequency(self, customer: Dict[str, Any]) -> str:
        """Calculate how frequently customer interacts with support."""
        total_tickets = customer.get("total_tickets", 0)
        tenure_days = self._calculate_tenure_days(customer.get("signup_date"))
        
        if tenure_days == 0:
            return "new_customer"
        
        tickets_per_month = total_tickets / (tenure_days / 30)
        
        if tickets_per_month > 2:
            return "high_frequency"
        elif tickets_per_month > 0.5:
            return "moderate_frequency"
        else:
            return "low_frequency"
    
    def _extract_issue_keywords(self, issue_type: str, source_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from issue for matching with knowledge base."""
        keywords = []
        
        # Extract from issue type
        keywords.extend(issue_type.split("_"))
        
        # Extract from source data
        if "category" in source_data:
            keywords.append(source_data["category"])
        if "subcategory" in source_data:
            keywords.append(source_data["subcategory"])
        if "tags" in source_data:
            keywords.extend(source_data["tags"])
        
        return [k.lower() for k in keywords if k]
    
    def _generate_support_insights(self, issues: List[Dict[str, Any]], 
                                 support_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall customer support insights."""
        insights = {
            "total_customers_affected": len(set(i.get("customer_id") for i in issues if i.get("customer_id"))),
            "high_risk_customers": [],
            "common_issue_patterns": {},
            "resource_allocation_recommendations": [],
            "escalation_predictions": []
        }
        
        # Identify high-risk customers
        customer_risk_scores = {}
        for issue in issues:
            customer_id = issue.get("customer_id")
            if customer_id:
                severity_weight = {"critical": 3, "high": 2, "medium": 1, "low": 0.5}.get(issue.get("severity"), 1)
                customer_risk_scores[customer_id] = customer_risk_scores.get(customer_id, 0) + severity_weight
        
        # Sort customers by risk score
        high_risk_customers = [(cid, score) for cid, score in customer_risk_scores.items() if score >= 3]
        high_risk_customers.sort(key=lambda x: x[1], reverse=True)
        insights["high_risk_customers"] = high_risk_customers[:5]
        
        # Identify common patterns
        issue_types = [i.get("type", "unknown") for i in issues]
        type_counts = {}
        for issue_type in issue_types:
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        insights["common_issue_patterns"] = dict(sorted(type_counts.items(), 
                                                       key=lambda x: x[1], 
                                                       reverse=True)[:5])
        
        # Resource allocation recommendations
        if type_counts.get("sla_violation", 0) > 2:
            insights["resource_allocation_recommendations"].append(
                "Increase staffing during peak hours to prevent SLA violations"
            )
        
        if type_counts.get("knowledge_base_gap", 0) > 1:
            insights["resource_allocation_recommendations"].append(
                "Allocate resources to knowledge base content creation"
            )
        
        if len(high_risk_customers) > 2:
            insights["resource_allocation_recommendations"].append(
                "Assign dedicated account managers to high-risk customers"
            )
        
        return insights


class CustomerSupportPlanActivity(BaseActivity):
    """
    Customer Support Planning Activity - Plan response strategies, account updates,
    and escalation workflows based on detected issues and analysis insights.
    """
    
    def __init__(self):
        super().__init__(activity_type="plan", domain="customer_support")
        self.description = "Plan customer support response strategies and workflows"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan customer support actions based on detected issues and analysis."""
        self.logger.info("Planning customer support response strategies")
        
        # Get detection and analysis results
        detection_results = context.get("detection_results", {})
        analysis_results = context.get("analysis_results", {})
        
        # Plan responses for each detected issue
        planned_actions = []
        for issue in detection_results.get("detected_issues", []):
            action_plan = await self._plan_issue_response(issue, analysis_results, context)
            planned_actions.append(action_plan)
        
        # Plan customer account updates
        account_updates = await self._plan_account_updates(analysis_results, context)
        
        # Plan escalation workflows
        escalation_workflows = await self._plan_escalation_workflows(analysis_results, context)
        
        # Plan follow-up actions
        follow_up_plans = await self._plan_follow_up_actions(analysis_results, context)
        
        # Create comprehensive planning result
        planning_result = {
            "planned_actions": planned_actions,
            "account_updates": account_updates,
            "escalation_workflows": escalation_workflows,
            "follow_up_plans": follow_up_plans,
            "planning_metadata": {
                "total_issues_planned": len(planned_actions),
                "high_priority_actions": sum(1 for action in planned_actions if action.get("priority") == "high"),
                "requires_escalation": sum(1 for action in planned_actions if action.get("escalate", False)),
                "planned_at": datetime.utcnow().isoformat(),
                "planner_version": "1.0"
            }
        }
        
        self.logger.info(f"Planned {len(planned_actions)} customer support actions")
        return planning_result
    
    async def _plan_issue_response(self, issue: Dict[str, Any], analysis_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan response strategy for a specific issue."""
        issue_id = issue.get("issue_id", "unknown")
        issue_type = issue.get("type", "")
        severity = issue.get("severity", "medium")
        
        # Get customer analysis for this issue
        customer_analysis = self._get_customer_analysis_for_issue(issue_id, analysis_results)
        
        # Determine response strategy
        response_strategy = self._determine_response_strategy(issue, customer_analysis)
        
        # Plan specific actions
        actions = []
        
        # 1. Immediate response actions
        immediate_actions = self._plan_immediate_actions(issue, customer_analysis, response_strategy)
        actions.extend(immediate_actions)
        
        # 2. Knowledge base actions
        kb_actions = self._plan_knowledge_base_actions(issue, customer_analysis)
        actions.extend(kb_actions)
        
        # 3. Account management actions
        account_actions = self._plan_account_management_actions(issue, customer_analysis)
        actions.extend(account_actions)
        
        # 4. Communication actions
        comm_actions = self._plan_communication_actions(issue, customer_analysis, response_strategy)
        actions.extend(comm_actions)
        
        return {
            "issue_id": issue_id,
            "issue_type": issue_type,
            "severity": severity,
            "response_strategy": response_strategy,
            "actions": actions,
            "priority": self._calculate_action_priority(issue, customer_analysis),
            "estimated_resolution_time": self._estimate_resolution_time(issue, customer_analysis),
            "escalate": self._should_escalate(issue, customer_analysis),
            "escalation_path": self._determine_escalation_path(issue, customer_analysis.get("customer"))
        }
    
    def _get_customer_analysis_for_issue(self, issue_id: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer analysis results for a specific issue."""
        issue_analyses = analysis_results.get("issue_analyses", [])
        for analysis in issue_analyses:
            if analysis.get("issue_id") == issue_id:
                return analysis
        return {}
    
    def _determine_response_strategy(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> str:
        """Determine the overall response strategy for an issue."""
        issue_type = issue.get("type", "")
        severity = issue.get("severity", "medium")
        customer = customer_analysis.get("customer", {})
        churn_risk = customer_analysis.get("risk_assessment", {}).get("churn_risk", "low")
        
        # High-value customer or high churn risk
        if customer.get("account_type") == "enterprise" or churn_risk == "high":
            return "white_glove_service"
        
        # Critical or urgent issues
        if severity in ["critical", "high"]:
            return "expedited_resolution"
        
        # Technical issues requiring expertise
        if "api" in issue_type or "technical" in issue_type:
            return "expert_consultation"
        
        # Standard issues
        return "standard_resolution"
    
    def _plan_immediate_actions(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any], strategy: str) -> List[Dict[str, Any]]:
        """Plan immediate response actions."""
        actions = []
        
        # Acknowledge receipt
        actions.append({
            "type": "acknowledge_ticket",
            "tool": "update_ticket_status",
            "parameters": {
                "ticket_id": issue.get("ticket_id"),
                "status": "acknowledged",
                "notes": f"Ticket received and being processed with {strategy} strategy"
            },
            "priority": "immediate",
            "estimated_time_minutes": 5
        })
        
        # Auto-response to customer
        if strategy == "white_glove_service":
            response_template = "premium_acknowledgment"
        elif issue.get("severity") in ["critical", "high"]:
            response_template = "urgent_acknowledgment"
        else:
            response_template = "standard_acknowledgment"
        
        actions.append({
            "type": "send_acknowledgment",
            "tool": "send_customer_response",
            "parameters": {
                "ticket_id": issue.get("ticket_id"),
                "customer_id": customer_analysis.get("customer", {}).get("id"),
                "response_text": f"Thank you for contacting support. We've received your {issue.get('type', 'request')} and are investigating.",
                "template_id": response_template
            },
            "priority": "immediate",
            "estimated_time_minutes": 10
        })
        
        return actions
    
    def _plan_knowledge_base_actions(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan knowledge base search and article suggestion actions."""
        actions = []
        
        # Search for relevant articles
        search_terms = self._extract_search_terms(issue)
        
        actions.append({
            "type": "search_knowledge_base",
            "tool": "search_knowledge_base",
            "parameters": {
                "query": " ".join(search_terms),
                "category": issue.get("category"),
                "max_results": 5
            },
            "priority": "high",
            "estimated_time_minutes": 15
        })
        
        return actions
    
    def _plan_account_management_actions(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan account management and update actions."""
        actions = []
        
        customer = customer_analysis.get("customer", {})
        risk_assessment = customer_analysis.get("risk_assessment", {})
        
        # Update customer health score if needed
        if risk_assessment.get("churn_risk") == "high":
            actions.append({
                "type": "update_health_score",
                "tool": "update_customer_account",
                "parameters": {
                    "customer_id": customer.get("id"),
                    "updates": {
                        "health_score": max(customer.get("health_score", 100) - 10, 0),
                        "notes": f"Health score adjusted due to support issue: {issue.get('type')}"
                    },
                    "reason": "Support issue impact on customer health"
                },
                "priority": "medium",
                "estimated_time_minutes": 5
            })
        
        # Plan account tier adjustments if needed
        if self._should_upgrade_support_tier(issue, customer_analysis):
            actions.append({
                "type": "upgrade_support_tier",
                "tool": "update_customer_account", 
                "parameters": {
                    "customer_id": customer.get("id"),
                    "updates": {
                        "support_tier": "premium",
                        "notes": "Support tier upgraded due to issue complexity"
                    },
                    "reason": "Issue complexity requires premium support"
                },
                "priority": "medium",
                "estimated_time_minutes": 10
            })
        
        return actions
    
    def _plan_communication_actions(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any], strategy: str) -> List[Dict[str, Any]]:
        """Plan customer communication actions."""
        actions = []
        
        customer = customer_analysis.get("customer", {})
        
        # Plan regular updates for high-value customers
        if strategy == "white_glove_service" or customer.get("account_type") == "enterprise":
            actions.append({
                "type": "schedule_progress_update",
                "tool": "create_follow_up_task",
                "parameters": {
                    "ticket_id": issue.get("ticket_id"),
                    "task_description": "Send progress update to customer",
                    "assigned_to": "account_manager", 
                    "task_type": "progress_update"
                },
                "priority": "medium",
                "estimated_time_minutes": 15
            })
        
        # Notify account manager for enterprise customers
        if customer.get("account_type") == "enterprise":
            actions.append({
                "type": "notify_account_manager",
                "tool": "notify_account_manager",
                "parameters": {
                    "customer_id": customer.get("id"),
                    "issue_summary": f"Support issue: {issue.get('type')} - {issue.get('severity')} priority",
                    "urgency": "high" if issue.get("severity") in ["critical", "high"] else "normal",
                    "recommended_action": "Monitor resolution progress and customer satisfaction"
                },
                "priority": "high",
                "estimated_time_minutes": 5
            })
        
        return actions
    
    async def _plan_account_updates(self, analysis_results: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan customer account updates based on analysis."""
        account_updates = []
        
        customer_analyses = analysis_results.get("customer_analyses", [])
        for customer_analysis in customer_analyses:
            customer = customer_analysis.get("customer", {})
            risk_assessment = customer_analysis.get("risk_assessment", {})
            
            # Plan churn prevention actions
            if risk_assessment.get("churn_risk") == "high":
                account_updates.append({
                    "customer_id": customer.get("id"),
                    "update_type": "churn_prevention",
                    "actions": [
                        {
                            "type": "assign_success_manager",
                            "description": "Assign dedicated customer success manager",
                            "priority": "high"
                        },
                        {
                            "type": "schedule_health_check",
                            "description": "Schedule account health check meeting",
                            "priority": "high"
                        }
                    ]
                })
            
            # Plan satisfaction improvement actions
            if customer.get("satisfaction_score", 5.0) < 3.0:
                account_updates.append({
                    "customer_id": customer.get("id"),
                    "update_type": "satisfaction_improvement",
                    "actions": [
                        {
                            "type": "executive_review",
                            "description": "Executive review of customer experience",
                            "priority": "medium"
                        },
                        {
                            "type": "personalized_outreach",
                            "description": "Personalized outreach to understand concerns",
                            "priority": "medium"
                        }
                    ]
                })
        
        return account_updates
    
    async def _plan_escalation_workflows(self, analysis_results: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan escalation workflows for complex issues."""
        escalation_workflows = []
        
        issue_analyses = analysis_results.get("issue_analyses", [])
        for issue_analysis in issue_analyses:
            expertise_gap = issue_analysis.get("expertise_gap", {})
            required_expertise = issue_analysis.get("required_expertise", [])
            
            if expertise_gap.get("gap_identified"):
                escalation_workflows.append({
                    "issue_id": issue_analysis.get("issue_id"),
                    "escalation_type": "expertise_gap",
                    "workflow": [
                        {
                            "step": "identify_specialist",
                            "description": f"Find specialist with {', '.join(required_expertise)} expertise",
                            "tool": "escalate_to_specialist",
                            "parameters": {
                                "specialist_type": required_expertise[0] if required_expertise else "technical_support"
                            }
                        },
                        {
                            "step": "transfer_context",
                            "description": "Transfer full context to specialist",
                            "tool": "update_ticket_status",
                            "parameters": {
                                "status": "escalated",
                                "notes": f"Escalated for {', '.join(required_expertise)} expertise"
                            }
                        }
                    ]
                })
        
        return escalation_workflows
    
    async def _plan_follow_up_actions(self, analysis_results: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan follow-up actions to ensure customer satisfaction."""
        follow_up_plans = []
        
        issue_analyses = analysis_results.get("issue_analyses", [])
        for issue_analysis in issue_analyses:
            estimated_resolution = issue_analysis.get("estimated_resolution_time", 24)
            
            # Plan satisfaction survey
            follow_up_plans.append({
                "issue_id": issue_analysis.get("issue_id"),
                "follow_up_type": "satisfaction_survey",
                "scheduled_hours_after_resolution": 24,
                "actions": [
                    {
                        "type": "send_satisfaction_survey",
                        "tool": "create_follow_up_task",
                        "parameters": {
                            "task_type": "satisfaction_survey",
                            "task_description": "Send customer satisfaction survey"
                        }
                    }
                ]
            })
            
            # Plan check-in for complex issues
            if estimated_resolution > 48:
                follow_up_plans.append({
                    "issue_id": issue_analysis.get("issue_id"),
                    "follow_up_type": "progress_check",
                    "scheduled_hours_after_start": 48,
                    "actions": [
                        {
                            "type": "progress_check_in",
                            "tool": "create_follow_up_task",
                            "parameters": {
                                "task_type": "check_in",
                                "task_description": "Check resolution progress with customer"
                            }
                        }
                    ]
                })
        
        return follow_up_plans
    
    def _extract_search_terms(self, issue: Dict[str, Any]) -> List[str]:
        """Extract relevant search terms from an issue."""
        terms = []
        
        # Add issue type
        issue_type = issue.get("type", "")
        if issue_type:
            terms.append(issue_type)
        
        # Extract from subject and description
        subject = issue.get("subject", "")
        description = issue.get("description", "")
        
        # Simple keyword extraction
        keywords = ["sso", "saml", "api", "rate limit", "billing", "authentication", "login", "error"]
        text = f"{subject} {description}".lower()
        
        for keyword in keywords:
            if keyword in text:
                terms.append(keyword)
        
        return list(set(terms))  # Remove duplicates
    
    def _should_upgrade_support_tier(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> bool:
        """Determine if customer support tier should be upgraded."""
        customer = customer_analysis.get("customer", {})
        current_tier = customer.get("support_tier", "community")
        
        # Don't upgrade if already premium
        if current_tier == "premium":
            return False
        
        # Upgrade for enterprise customers with complex issues
        if customer.get("account_type") == "enterprise" and issue.get("severity") in ["critical", "high"]:
            return True
        
        # Upgrade for repeat issues
        issue_history = customer_analysis.get("issue_history", [])
        if len(issue_history) > 3:
            return True
        
        return False
    
    def _calculate_action_priority(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> str:
        """Calculate priority level for actions."""
        severity = issue.get("severity", "medium")
        customer = customer_analysis.get("customer", {})
        
        if severity == "critical" or customer.get("account_type") == "enterprise":
            return "critical"
        elif severity == "high" or customer.get("support_tier") == "premium":
            return "high"
        else:
            return "medium"
    
    def _estimate_resolution_time(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> int:
        """Estimate resolution time in hours."""
        base_times = {
            "billing": 4,
            "api": 8,
            "technical": 12,
            "authentication": 6,
            "sso": 8,
            "general": 6
        }
        
        issue_type = issue.get("type", "general")
        base_time = base_times.get(issue_type, 6)
        
        # Adjust for complexity
        if issue.get("severity") == "critical":
            base_time *= 0.5  # Expedited
        elif issue.get("severity") == "low":
            base_time *= 1.5  # Lower priority
        
        # Adjust for customer tier
        customer = customer_analysis.get("customer", {})
        if customer.get("support_tier") == "premium":
            base_time *= 0.75  # Faster resolution
        
        return int(base_time)
    
    def _should_escalate(self, issue: Dict[str, Any], customer_analysis: Dict[str, Any]) -> bool:
        """Determine if issue should be escalated."""
        severity = issue.get("severity", "medium")
        customer = customer_analysis.get("customer", {})
        expertise_gap = customer_analysis.get("expertise_gap", {}).get("gap_identified", False)
        
        # Escalate critical issues
        if severity == "critical":
            return True
        
        # Escalate for enterprise customers with high severity
        if customer.get("account_type") == "enterprise" and severity == "high":
            return True
        
        # Escalate when expertise gap identified
        if expertise_gap:
            return True
        
        return False
    
    def _determine_escalation_path(self, issue: Dict[str, Any], customer: Optional[Dict[str, Any]]) -> str:
        """Determine escalation path for the issue."""
        severity = issue.get("severity", "medium")
        issue_type = issue.get("type", "")
        
        if not customer:
            return "standard_escalation"
        
        account_value = customer.get("account_value", 0)
        support_tier = customer.get("support_tier", "community")
        
        # Critical issues or high-value customers
        if severity == "critical" or account_value > 20000:
            return "immediate_manager_escalation"
        
        # Premium support customers
        if support_tier == "premium":
            return "account_manager_escalation"
        
        # Technical escalation
        if "technical" in issue_type or "api" in issue_type:
            return "technical_lead_escalation"
        
        return "standard_escalation"


def register_customer_support_domain():
    """Register customer support domain components."""
    print("Registering customer support domain...")
    
    # Register enhanced activities (these override the generic ones)
    # Note: In a full implementation, you might register these differently
    
    print("Customer support domain registered successfully!")


if __name__ == "__main__":
    # Demonstrate the customer support domain
    register_customer_support_domain()
    print("Customer support domain setup complete!")