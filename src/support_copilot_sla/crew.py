from typing import Any, Dict

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from support_copilot_sla.tools.schedule_callback import ScheduleCallbackTool
from support_copilot_sla.workflow import handle_sla_support_ticket


schedule_callback_tool = ScheduleCallbackTool()


@CrewBase
class SupportCopilotSlaCrew:
    """Support Copilot SLA crew for PII-safe ticket handling."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def draft_reply_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["draft_reply_agent"],
            verbose=True,
        )

    @task
    def draft_reply_task(self) -> Task:
        return Task(
            config=self.tasks_config["draft_reply_task"],
            agent=self.draft_reply_agent(),
        )

    @task
    def handle_sla_support_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["handle_sla_support_ticket_task"],
            agent=self.draft_reply_agent(),
            tools=[schedule_callback_tool],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_handle_sla_support_ticket(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the Handle SLA Support Ticket workflow with PII-safe output.

    When ``use_llm`` is True, the Draft Reply agent generates the reply via
    CrewAI. Otherwise a deterministic template is used (for offline tests).
    """
    use_llm = inputs.get("use_llm", False)
    ticket_id = inputs["ticket_id"]
    customer_email = inputs["customer_email"]
    issue_summary = inputs["issue_summary"]
    preferred_time = inputs.get("preferred_time", "next business day")

    if use_llm:
        crew_result = SupportCopilotSlaCrew().crew().kickoff(inputs=inputs)
        reply_draft = str(crew_result)
    else:
        reply_draft = (
            "Hello,\n\n"
            f"Thank you for reaching out regarding: {issue_summary}\n\n"
            "We have received your request and will follow up shortly. "
            "If we need additional contact details or store access, please "
            "submit them via our secure form: "
            "https://support.example.com/secure-intake\n\n"
            "Best regards,\nSupport Team"
        )

    return handle_sla_support_ticket(
        ticket_id=ticket_id,
        customer_email=customer_email,
        issue_summary=issue_summary,
        preferred_time=preferred_time,
        reply_draft=reply_draft,
    )
