"""
Expense Report tools for the DAPERL framework.
Implements tools for expense report processing, validation, and workflow automation.
"""
from temporalio import activity

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from daperl.core.tools import BaseTool, ToolRegistry, ToolInfo


class RequestReceiptTool(BaseTool):
    """Tool for requesting missing receipts from employees."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        activity.logger.info(f"In RequestReceiptTool.execute with arguments: {arguments}")
        
        """Request missing receipt from employee."""
        report_id = arguments.get("report_id")
        item_id = arguments.get("item_id")
        employee_id = arguments.get("employee_id")
        deadline = arguments.get("deadline")
        
        if not all([report_id, employee_id]):
            return self.create_response(
                success=False,
                data={"error": "report_id and employee_id are required"},
                additional_notes="Missing required parameters"
            )
        
        # Read the expense reports data
        data_file_path = os.path.join(os.path.dirname(__file__), "data", "expense_reports.json")
        try:
            with open(data_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return self.create_response(
                success=False,
                data={"error": "expense_reports.json file not found"},
                additional_notes="Could not load expense reports data"
            )
        except json.JSONDecodeError:
            return self.create_response(
                success=False,
                data={"error": "Invalid JSON in expense_reports.json"},
                additional_notes="Could not parse expense reports data"
            )
        
        # Find the report and update status
        reports = data.get("reports", [])
        report_found = False
        employee_name = None
        
        for report in reports:
            if report.get("report_id") == report_id:
                report_found = True
                employee_name = report.get("employee_name")
                
                # Update report status to awaiting_receipt
                report["status"] = "awaiting_receipt"
                report["last_updated"] = datetime.utcnow().isoformat()
                
                # Add note about receipt request
                if "notes" not in report:
                    report["notes"] = []
                
                note_text = f"Receipt requested for "
                if item_id:
                    note_text += f"item {item_id}"
                else:
                    note_text += "missing items"
                
                if deadline:
                    note_text += f" - Due by {deadline}"
                
                report["notes"].append({
                    "text": note_text,
                    "added_at": datetime.utcnow().isoformat(),
                    "added_by": "daperl_system"
                })
                
                break
        
        if not report_found:
            return self.create_response(
                success=False,
                data={"error": f"Report {report_id} not found"},
                additional_notes="Could not find expense report in database"
            )
        
        # Write updated data back to file
        try:
            with open(data_file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            return self.create_response(
                success=False,
                data={"error": f"Failed to write data: {str(e)}"},
                additional_notes="Could not save updated expense report data"
            )
        
        # Calculate default deadline if not provided
        if not deadline:
            deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        result_data = {
            "report_id": report_id,
            "item_id": item_id,
            "employee_id": employee_id,
            "employee_name": employee_name,
            "deadline": deadline,
            "request_sent_at": datetime.utcnow().isoformat(),
            "notification_method": "email",
            "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        activity.logger.info(f"Requested receipt for report {report_id} from {employee_name}")
        
        return self.create_response(
            success=True,
            data=result_data,
            additional_notes=f"Receipt request sent to {employee_name} for report {report_id}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="request_receipt",
            description="Request missing receipt from employee with deadline",
            parameters=["report_id", "item_id", "employee_id", "deadline"],
            domain=self.domain,
            tool_class=RequestReceiptTool
        )


class CalculateMileageTool(BaseTool):
    """Tool for calculating mileage reimbursement amounts."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        activity.logger.info(f"In CalculateMileageTool.execute with arguments: {arguments}")
        
        """Calculate mileage reimbursement amount."""
        report_id = arguments.get("report_id")
        item_id = arguments.get("item_id")
        miles = arguments.get("miles")
        rate_per_mile = arguments.get("rate_per_mile")
        
        if not report_id:
            return self.create_response(
                success=False,
                data={"error": "report_id is required"},
                additional_notes="Missing required parameters"
            )
        
        # Read the expense reports data
        data_file_path = os.path.join(os.path.dirname(__file__), "data", "expense_reports.json")
        try:
            with open(data_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return self.create_response(
                success=False,
                data={"error": "expense_reports.json file not found"},
                additional_notes="Could not load expense reports data"
            )
        except json.JSONDecodeError:
            return self.create_response(
                success=False,
                data={"error": "Invalid JSON in expense_reports.json"},
                additional_notes="Could not parse expense reports data"
            )
        
        # Get default mileage rate from policy if not provided
        if not rate_per_mile:
            rate_per_mile = data.get("policy", {}).get("mileage_rate", 0.67)
        
        # Find the report and calculate mileage
        reports = data.get("reports", [])
        report_found = False
        calculation_performed = False
        calculated_amount = 0.0
        
        for report in reports:
            if report.get("report_id") == report_id:
                report_found = True
                
                # Find mileage items and calculate
                items = report.get("items", [])
                for item in items:
                    # If item_id specified, only process that item
                    if item_id and item.get("id") != item_id:
                        continue
                    
                    # Check if this is a mileage item
                    if item.get("category") == "Mileage":
                        item_miles = miles if miles else item.get("miles")
                        
                        if item_miles:
                            calculated_amount = float(item_miles) * float(rate_per_mile)
                            item["amount"] = round(calculated_amount, 2)
                            item["rate_per_mile"] = rate_per_mile
                            item["calculated_at"] = datetime.utcnow().isoformat()
                            calculation_performed = True
                            
                            activity.logger.info(f"Calculated mileage: {item_miles} miles × ${rate_per_mile} = ${calculated_amount}")
                
                # Recalculate report total
                if calculation_performed:
                    total = sum(item.get("amount", 0) for item in items if item.get("amount") is not None)
                    report["total"] = round(total, 2)
                    report["last_updated"] = datetime.utcnow().isoformat()
                    
                    # Add calculation note
                    if "notes" not in report:
                        report["notes"] = []
                    report["notes"].append({
                        "text": f"Mileage calculated automatically at ${rate_per_mile}/mile",
                        "added_at": datetime.utcnow().isoformat(),
                        "added_by": "daperl_system"
                    })
                
                break
        
        if not report_found:
            return self.create_response(
                success=False,
                data={"error": f"Report {report_id} not found"},
                additional_notes="Could not find expense report in database"
            )
        
        if not calculation_performed:
            return self.create_response(
                success=False,
                data={"error": "No mileage items found to calculate"},
                additional_notes="Report does not contain mileage items or miles value missing"
            )
        
        # Write updated data back to file
        try:
            with open(data_file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            return self.create_response(
                success=False,
                data={"error": f"Failed to write data: {str(e)}"},
                additional_notes="Could not save updated expense report data"
            )
        
        result_data = {
            "report_id": report_id,
            "item_id": item_id,
            "miles": miles,
            "rate_per_mile": rate_per_mile,
            "calculated_amount": calculated_amount,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        activity.logger.info(f"Calculated mileage for report {report_id}: ${calculated_amount}")
        
        return self.create_response(
            success=True,
            data=result_data,
            additional_notes=f"Mileage calculated: ${calculated_amount:.2f}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="calculate_mileage",
            description="Calculate mileage reimbursement amount based on miles and rate",
            parameters=["report_id", "item_id", "miles", "rate_per_mile"],
            domain=self.domain,
            tool_class=CalculateMileageTool
        )


class FlagForManualReviewTool(BaseTool):
    """Tool for flagging expense reports for manual review."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        activity.logger.info(f"In FlagForManualReviewTool.execute with arguments: {arguments}")
        
        """Flag expense report for manual manager review."""
        report_id = arguments.get("report_id")
        reason = arguments.get("reason")
        severity = arguments.get("severity", "medium")
        assigned_to = arguments.get("assigned_to", "finance_manager")
        
        if not all([report_id, reason]):
            return self.create_response(
                success=False,
                data={"error": "report_id and reason are required"},
                additional_notes="Missing required parameters"
            )
        
        # Read the expense reports data
        data_file_path = os.path.join(os.path.dirname(__file__), "data", "expense_reports.json")
        try:
            with open(data_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return self.create_response(
                success=False,
                data={"error": "expense_reports.json file not found"},
                additional_notes="Could not load expense reports data"
            )
        except json.JSONDecodeError:
            return self.create_response(
                success=False,
                data={"error": "Invalid JSON in expense_reports.json"},
                additional_notes="Could not parse expense reports data"
            )
        
        # Find the report and flag for review
        reports = data.get("reports", [])
        report_found = False
        employee_name = None
        
        for report in reports:
            if report.get("report_id") == report_id:
                report_found = True
                employee_name = report.get("employee_name")
                
                # Update report status
                report["status"] = "flagged_for_review"
                report["last_updated"] = datetime.utcnow().isoformat()
                report["assigned_to"] = assigned_to
                report["review_severity"] = severity
                
                # Add flagging note
                if "notes" not in report:
                    report["notes"] = []
                report["notes"].append({
                    "text": f"FLAGGED FOR REVIEW [{severity.upper()}]: {reason}",
                    "added_at": datetime.utcnow().isoformat(),
                    "added_by": "daperl_system",
                    "severity": severity
                })
                
                break
        
        if not report_found:
            return self.create_response(
                success=False,
                data={"error": f"Report {report_id} not found"},
                additional_notes="Could not find expense report in database"
            )
        
        # Write updated data back to file
        try:
            with open(data_file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            return self.create_response(
                success=False,
                data={"error": f"Failed to write data: {str(e)}"},
                additional_notes="Could not save updated expense report data"
            )
        
        result_data = {
            "report_id": report_id,
            "employee_name": employee_name,
            "reason": reason,
            "severity": severity,
            "assigned_to": assigned_to,
            "flagged_at": datetime.utcnow().isoformat(),
            "flag_id": f"FLAG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        activity.logger.info(f"Flagged report {report_id} for manual review: {reason}")
        
        return self.create_response(
            success=True,
            data=result_data,
            additional_notes=f"Report {report_id} flagged for {assigned_to} review with {severity} severity"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="flag_for_manual_review",
            description="Flag expense report for manual manager review with reason and severity",
            parameters=["report_id", "reason", "severity", "assigned_to"],
            domain=self.domain,
            tool_class=FlagForManualReviewTool
        )


class AutoApproveTool(BaseTool):
    """Tool for auto-approving compliant expense reports."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        activity.logger.info(f"In AutoApproveTool.execute with arguments: {arguments}")
        
        """Auto-approve compliant expense report."""
        report_id = arguments.get("report_id")
        approver = arguments.get("approver", "daperl_system")
        notes = arguments.get("notes", "Auto-approved - meets all policy requirements")
        
        if not report_id:
            return self.create_response(
                success=False,
                data={"error": "report_id is required"},
                additional_notes="Missing required parameters"
            )
        
        # Read the expense reports data
        data_file_path = os.path.join(os.path.dirname(__file__), "data", "expense_reports.json")
        try:
            with open(data_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return self.create_response(
                success=False,
                data={"error": "expense_reports.json file not found"},
                additional_notes="Could not load expense reports data"
            )
        except json.JSONDecodeError:
            return self.create_response(
                success=False,
                data={"error": "Invalid JSON in expense_reports.json"},
                additional_notes="Could not parse expense reports data"
            )
        
        # Find the report and approve it
        reports = data.get("reports", [])
        report_found = False
        employee_name = None
        report_total = 0.0
        
        for report in reports:
            if report.get("report_id") == report_id:
                report_found = True
                employee_name = report.get("employee_name")
                report_total = report.get("total", 0.0)
                
                # Update report status to approved
                previous_status = report.get("status")
                report["status"] = "approved"
                report["approved_by"] = approver
                report["approved_at"] = datetime.utcnow().isoformat()
                report["last_updated"] = datetime.utcnow().isoformat()
                
                # Add approval note
                if "notes" not in report:
                    report["notes"] = []
                report["notes"].append({
                    "text": f"APPROVED: {notes}",
                    "added_at": datetime.utcnow().isoformat(),
                    "added_by": approver,
                    "previous_status": previous_status
                })
                
                break
        
        if not report_found:
            return self.create_response(
                success=False,
                data={"error": f"Report {report_id} not found"},
                additional_notes="Could not find expense report in database"
            )
        
        # Write updated data back to file
        try:
            with open(data_file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            return self.create_response(
                success=False,
                data={"error": f"Failed to write data: {str(e)}"},
                additional_notes="Could not save updated expense report data"
            )
        
        result_data = {
            "report_id": report_id,
            "employee_name": employee_name,
            "total_amount": report_total,
            "approver": approver,
            "approved_at": datetime.utcnow().isoformat(),
            "approval_notes": notes,
            "reimbursement_status": "scheduled"
        }
        
        activity.logger.info(f"Auto-approved report {report_id} for {employee_name}: ${report_total}")
        
        return self.create_response(
            success=True,
            data=result_data,
            additional_notes=f"Report {report_id} approved for ${report_total:.2f} reimbursement"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="auto_approve",
            description="Auto-approve compliant expense report for reimbursement",
            parameters=["report_id", "approver", "notes"],
            domain=self.domain,
            tool_class=AutoApproveTool
        )


class SendNotificationTool(BaseTool):
    """Tool for sending notifications to employees and managers."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        activity.logger.info(f"In SendNotificationTool.execute with arguments: {arguments}")
        
        """Send notification to employee or manager (mocked implementation)."""
        recipient_id = arguments.get("recipient_id")
        notification_type = arguments.get("notification_type", "email")
        message = arguments.get("message")
        urgency = arguments.get("urgency", "normal")
        
        if not all([recipient_id, message]):
            return self.create_response(
                success=False,
                data={"error": "recipient_id and message are required"},
                additional_notes="Missing required parameters"
            )
        
        # Mock implementation - in real usage would integrate with email/Slack/SMS systems
        notification_methods = {
            "email": "Email",
            "slack": "Slack",
            "sms": "SMS",
            "in_app": "In-App Notification"
        }
        
        method_name = notification_methods.get(notification_type, "Email")
        
        # Determine expected delivery time based on urgency
        delivery_time = {
            "critical": "Immediate",
            "high": "Within 5 minutes",
            "normal": "Within 15 minutes",
            "low": "Within 1 hour"
        }.get(urgency, "Within 15 minutes")
        
        result_data = {
            "notification_id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "recipient_id": recipient_id,
            "notification_type": notification_type,
            "method": method_name,
            "message": message,
            "urgency": urgency,
            "sent_at": datetime.utcnow().isoformat(),
            "delivery_status": "sent",
            "expected_delivery": delivery_time,
            "message_length": len(message)
        }
        
        activity.logger.info(f"Sent {method_name} notification to {recipient_id} with {urgency} urgency")
        
        return self.create_response(
            success=True,
            data=result_data,
            additional_notes=f"Notification sent via {method_name} to {recipient_id}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="send_notification",
            description="Send notification to employee or manager via email, Slack, or SMS",
            parameters=["recipient_id", "notification_type", "message", "urgency"],
            domain=self.domain,
            tool_class=SendNotificationTool
        )


def register_expense_reports_tools(domain: str = "expense_reports"):
    """Register expense report tools for a domain."""
    print(f"Registering expense report tools for domain: {domain}")
    
    tools = [
        RequestReceiptTool,
        CalculateMileageTool,
        FlagForManualReviewTool,
        AutoApproveTool,
        SendNotificationTool
    ]
    
    for tool_class in tools:
        ToolRegistry.register_tool(tool_class, domain)
        print(f"  ✅ Registered: {tool_class.__name__}")
    
    print(f"Expense report tools registered successfully for {domain}!")


if __name__ == "__main__":
    # Register expense report tools
    register_expense_reports_tools()
    
    # List registered tools
    print("\nRegistered Expense Report Tools:")
    for tool in ToolRegistry.get_tools_for_domain("expense_reports"):
        print(f"  - {tool['name']}: {tool['description']}")
