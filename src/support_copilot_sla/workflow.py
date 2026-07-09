"""Handle SLA Support Ticket workflow — PII-safe output assembly."""

from typing import Any, Dict

from support_copilot_sla.tools.schedule_callback import ScheduleCallbackTool


def build_callback_output(
    callback_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the public callback object for workflow output.

    Excludes raw ``customer_email``; only non-PII identifiers are returned.
    """
    return {
        "user_id": callback_result["user_id"],
        "masked_email": callback_result["masked_email"],
        "scheduled_at": callback_result["scheduled_at"],
        "preferred_time": callback_result.get("preferred_time"),
        "status": callback_result.get("status", "confirmed"),
    }


def handle_sla_support_ticket(
    ticket_id: str,
    customer_email: str,
    issue_summary: str,
    preferred_time: str,
    reply_draft: str,
) -> Dict[str, Any]:
    """
    Execute the Handle SLA Support Ticket workflow.

    The ``customer_email`` is used internally for scheduling but is never
    included in the final workflow output.
    """
    callback_tool = ScheduleCallbackTool()
    callback_result = callback_tool._run(
        customer_email=customer_email,
        preferred_time=preferred_time,
    )

    return {
        "workflow": "support-copilot-sla",
        "ticket_id": ticket_id,
        "issue_summary": issue_summary,
        "reply_draft": reply_draft,
        "callback": build_callback_output(callback_result),
    }
