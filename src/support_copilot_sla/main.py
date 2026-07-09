import json
import os

import neatlogs
from dotenv import load_dotenv

from support_copilot_sla.crew import run_handle_sla_support_ticket

load_dotenv()

neatlogs.init(
    api_key=os.getenv("NEATLOGS_API_KEY", "test-key"),
    tags=["support-copilot-sla"],
    enable_pii_masking=True,
)


def run():
    inputs = {
        "ticket_id": "TKT-48291",
        "customer_email": "maya.patel@example.com",
        "customer_name": "Maya",
        "issue_summary": "Store checkout failing with 500 error on payment step",
        "preferred_time": "tomorrow 2-4pm EST",
        "use_llm": False,
    }
    result = run_handle_sla_support_ticket(inputs)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
