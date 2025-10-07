from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool
from pydantic import BaseModel, Field
from job_posting.research_agent import ResearchAgent
import logging

# Configure logging
logger = logging.getLogger(__name__)

web_search_tool = WebsiteSearchTool()
seper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path='job_description_example.md',
    description='A tool to read the job description example file.'
)

class ResearchRoleRequirements(BaseModel):
    """Research role requirements model"""
    skills: List[str] = Field(..., description="List of recommended skills for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    experience: List[str] = Field(..., description="List of recommended experience for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    qualities: List[str] = Field(..., description="List of recommended qualities for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")

@CrewBase
class JobPostingCrew:
    """JobPosting crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        # Initialize the custom research agent wrapper for context management
        self._research_agent_wrapper = None
        logger.info("JobPostingCrew initialized with context management support")

    @agent
    def research_agent(self) -> Agent:
        base_agent = Agent(
            config=self.agents_config['research_agent'],
            tools=[web_search_tool, seper_dev_tool],
            verbose=True
        )
        
        # Initialize the ResearchAgent wrapper if not already done
        if self._research_agent_wrapper is None:
            self._research_agent_wrapper = ResearchAgent(base_agent)
            logger.info("ResearchAgent wrapper initialized for context propagation")
        
        return base_agent
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['writer_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True
        )
    
    @agent
    def review_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['review_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True
        )
    
    @task
    def research_company_culture_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_company_culture_task'],
            agent=self.research_agent()
        )

    @task
    def research_role_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_role_requirements_task'],
            agent=self.research_agent(),
            output_json=ResearchRoleRequirements
        )

    @task
    def draft_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_job_posting_task'],
            agent=self.writer_agent()
        )

    @task
    def review_and_edit_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_and_edit_job_posting_task'],
            agent=self.review_agent()
        )

    @task
    def industry_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['industry_analysis_task'],
            agent=self.research_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JobPostingCrew"""
        crew_instance = Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
        
        logger.info("Crew created with sequential processing and context management enabled")
        return crew_instance
    
    def get_research_context(self):
        """
        Get the current research context from the ResearchAgent.
        
        Returns:
            Dictionary containing all context data collected during research
        """
        if self._research_agent_wrapper is None:
            logger.warning("ResearchAgent wrapper not initialized")
            return {}
        
        context = self._research_agent_wrapper.get_context()
        logger.info(f"Retrieved research context with {len(context.get('search_results', []))} search results")
        return context
    
    def execute_research_search(self, query: str, search_type: str, tool_name: str = 'web_search'):
        """
        Execute a research search with context propagation.
        
        Args:
            query: Search query
            search_type: Type of search (e.g., 'company_culture', 'role_skills')
            tool_name: Tool to use for search
            
        Returns:
            Search results with updated context
        """
        if self._research_agent_wrapper is None:
            # Initialize wrapper if not already done
            self._research_agent_wrapper = ResearchAgent(self.research_agent())
            logger.info("ResearchAgent wrapper initialized via execute_research_search")
        
        result = self._research_agent_wrapper.execute_search(query, search_type, tool_name)
        logger.info(f"Executed search for {search_type}: success={result['success']}")
        return result
    
    def compose_research_report(self, report_type: str = 'comprehensive'):
        """
        Compose a research report with context validation.
        
        Args:
            report_type: Type of report to generate
            
        Returns:
            Generated report
            
        Raises:
            ContextPropagationError: If required context is missing
        """
        if self._research_agent_wrapper is None:
            logger.error("ResearchAgent wrapper not initialized - cannot compose report")
            raise ValueError("ResearchAgent not initialized. Execute searches first.")
        
        logger.info(f"Composing {report_type} report with context validation")
        report = self._research_agent_wrapper.compose_report(report_type)
        return report
    
    def update_research_context(self, key: str, value):
        """
        Manually update the research context.
        
        Args:
            key: Context key to update
            value: New value
        """
        if self._research_agent_wrapper is None:
            self._research_agent_wrapper = ResearchAgent(self.research_agent())
            logger.info("ResearchAgent wrapper initialized via update_research_context")
        
        self._research_agent_wrapper.update_context(key, value)
        logger.info(f"Research context updated: {key}")
    
    def validate_research_context(self):
        """
        Validate that all required context data is present.
        
        Returns:
            List of missing context fields (empty if all required data is present)
        """
        if self._research_agent_wrapper is None:
            logger.warning("ResearchAgent wrapper not initialized - returning all required fields as missing")
            return ResearchAgent.REQUIRED_CONTEXT_KEYS
        
        missing = self._research_agent_wrapper._validate_context()
        
        if missing:
            logger.warning(f"Context validation found missing fields: {missing}")
        else:
            logger.info("Context validation passed - all required data present")
        
        return missing