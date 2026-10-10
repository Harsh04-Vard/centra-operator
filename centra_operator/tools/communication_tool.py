"""
Communication Dispatcher Tool:
Handles outbound company emails, candidate communication, and Slack/Teams broadcast channels.
"""

from typing import Any, Dict, List, Optional
import uuid
import time
from centra_operator.tools.base import BaseTool, ToolResult
from centra_operator.engine.state import RiskLevel

class EmailDispatcherTool(BaseTool):
    name = "email_dispatcher"
    description = "Send external transactional emails to employees, candidates, and customers."
    risk_level = RiskLevel.HIGH  # High risk: external blast radius
    requires_confirmation = True

    def __init__(self):
        self.outbox: List[Dict[str, Any]] = []

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        recipient = params.get("to")
        subject = params.get("subject", "Notification from Acme Enterprise")
        body = params.get("body", "")
        
        if not recipient or "@" not in recipient:
            return ToolResult(
                success=False,
                output=None,
                error=f"Invalid email address: {recipient}"
            )

        msg_id = f"msg-{uuid.uuid4().hex[:10]}"
        record = {
            "message_id": msg_id,
            "to": recipient,
            "subject": subject,
            "body": body,
            "timestamp": time.time(),
            "status": "DELIVERED"
        }
        self.outbox.append(record)

        return ToolResult(
            success=True,
            output=f"Email successfully dispatched to {recipient} (Message ID: {msg_id})",
            evidence={
                "message_id": msg_id,
                "recipient": recipient,
                "subject": subject,
                "delivery_status": "DELIVERED"
            }
        )

class SlackNotifierTool(BaseTool):
    name = "slack_notifier"
    description = "Broadcast structured notifications and audit updates to internal Slack channels."
    risk_level = RiskLevel.LOW

    def __init__(self):
        self.channel_history: Dict[str, List[Dict[str, Any]]] = {}

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        channel = params.get("channel", "#general")
        message = params.get("message", "")
        
        entry = {
            "channel": channel,
            "message": message,
            "timestamp": time.time()
        }
        if channel not in self.channel_history:
            self.channel_history[channel] = []
        self.channel_history[channel].append(entry)

        return ToolResult(
            success=True,
            output=f"Broadcast message to {channel}",
            evidence={"channel": channel, "status": "BROADCAST_SUCCESS"}
        )
