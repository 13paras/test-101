"""Schedule Callback tool — returns masked contact info, never raw PII."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from neatlogs.pii import mask_email


class ScheduleCallbackInput(BaseModel):
    """Input schema for scheduling a customer callback."""

    customer_email: str = Field(..., description="Customer email (used internally only)")
    preferred_time: str = Field(..., description="Customer's preferred callback window")


class ScheduleCallbackTool(BaseTool):
    name: str = "Schedule Callback"
    description: str = (
        "Schedule a callback for a support ticket. Returns a confirmation with "
        "an internal user_id and masked email — never the raw email address."
    )
    args_schema: Type[BaseModel] = ScheduleCallbackInput

    def _run(self, customer_email: str, preferred_time: str) -> dict:
        user_id = f"usr_{hashlib.sha256(customer_email.encode()).hexdigest()[:12]}"
        scheduled_at = (
            datetime.now(timezone.utc) + timedelta(hours=24)
        ).isoformat()

        return {
            "user_id": user_id,
            "masked_email": mask_email(customer_email),
            "scheduled_at": scheduled_at,
            "preferred_time": preferred_time,
            "status": "confirmed",
        }
