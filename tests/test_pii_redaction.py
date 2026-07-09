"""Tests for PII redaction in support-copilot-sla workflow and neatlogs SDK."""

import json
import unittest

from neatlogs.pii import mask_email, mask_pii_in_data, sanitize_span_payload
from support_copilot_sla.crew import run_handle_sla_support_ticket
from support_copilot_sla.tools.schedule_callback import ScheduleCallbackTool


class TestPIIMasking(unittest.TestCase):
    def test_mask_email(self):
        self.assertEqual(mask_email("maya.patel@example.com"), "m***@example.com")

    def test_sanitize_span_payload_redacts_emails(self):
        payload = {
            "messages": [{"role": "user", "content": "Contact maya.patel@example.com"}],
            "completion": "Sent to maya.patel@example.com",
        }
        sanitized = sanitize_span_payload(payload)
        self.assertNotIn("maya.patel@example.com", json.dumps(sanitized))
        self.assertIn("m***@example.com", json.dumps(sanitized))

    def test_mask_pii_in_data_excludes_customer_email(self):
        data = {
            "callback": {
                "customer_email": "maya.patel@example.com",
                "user_id": "usr_abc123",
            }
        }
        masked = mask_pii_in_data(data)
        self.assertNotIn("customer_email", masked["callback"])
        self.assertEqual(masked["callback"]["user_id"], "usr_abc123")


class TestScheduleCallbackTool(unittest.TestCase):
    def test_returns_masked_email_not_raw(self):
        tool = ScheduleCallbackTool()
        result = tool._run(
            customer_email="maya.patel@example.com",
            preferred_time="tomorrow 2pm",
        )
        self.assertNotIn("customer_email", result)
        self.assertEqual(result["masked_email"], "m***@example.com")
        self.assertTrue(result["user_id"].startswith("usr_"))


class TestHandleSlaSupportTicketWorkflow(unittest.TestCase):
    def test_workflow_output_excludes_customer_email(self):
        result = run_handle_sla_support_ticket(
            {
                "ticket_id": "TKT-48291",
                "customer_email": "maya.patel@example.com",
                "customer_name": "Maya",
                "issue_summary": "Checkout failing",
                "preferred_time": "tomorrow 2pm",
                "use_llm": False,
            }
        )
        output_json = json.dumps(result)
        self.assertNotIn("customer_email", result["callback"])
        self.assertNotIn("maya.patel@example.com", output_json)
        self.assertIn("masked_email", result["callback"])
        self.assertEqual(result["callback"]["masked_email"], "m***@example.com")

    def test_reply_draft_avoids_customer_name(self):
        result = run_handle_sla_support_ticket(
            {
                "ticket_id": "TKT-48291",
                "customer_email": "maya.patel@example.com",
                "customer_name": "Maya",
                "issue_summary": "Checkout failing",
                "use_llm": False,
            }
        )
        self.assertNotIn("Maya", result["reply_draft"])
        self.assertIn("Hello", result["reply_draft"])
        self.assertIn("secure-intake", result["reply_draft"])


if __name__ == "__main__":
    unittest.main()
