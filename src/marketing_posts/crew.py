from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool

# Uncomment the following line to use an example of a custom tool
# from marketing_posts.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field
import random

class MarketStrategy(BaseModel):
	"""Market strategy model"""
	name: str = Field(..., description="Name of the market strategy")
	tatics: List[str] = Field(..., description="List of tactics to be used in the market strategy")
	channels: List[str] = Field(..., description="List of channels to be used in the market strategy")
	KPIs: List[str] = Field(..., description="List of KPIs to be used in the market strategy")

class CampaignIdea(BaseModel):
	"""Campaign idea model"""
	name: str = Field(..., description="Name of the campaign idea")
	description: str = Field(..., description="Description of the campaign idea")
	audience: str = Field(..., description="Audience of the campaign idea")
	channel: str = Field(..., description="Channel of the campaign idea")

class Copy(BaseModel):
	"""Copy model"""
	title: str = Field(..., description="Title of the copy")
	body: str = Field(..., description="Body of the copy")

class WeatherReport(BaseModel):
	"""Weather report model"""
	location: str = Field(..., description="Location of the weather report")
	temperature: float = Field(..., description="Temperature value")
	unit: str = Field(..., description="Temperature unit (fahrenheit or celsius)")
	context: str = Field(..., description="Contextual information about the weather")

@tool("get_current_weather")
def get_current_weather(location: str, unit: str = "fahrenheit") -> dict:
	"""
	Get the current weather for a specific location.
	
	Args:
		location: The city or location to get weather for
		unit: The temperature unit (fahrenheit or celsius)
	
	Returns:
		A dictionary with temperature and basic weather info
	"""
	# Simulated weather data for demonstration
	# In production, this would call a real weather API
	base_temp = random.uniform(50, 85) if unit.lower() == "fahrenheit" else random.uniform(10, 30)
	
	return {
		"location": location,
		"temperature": round(base_temp, 1),
		"unit": unit,
		"humidity": random.randint(40, 80),
		"conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Clear"])
	}

@CrewBase
class MarketingPostsCrew():
	"""MarketingPosts crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def lead_market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_market_analyst'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False,
		)

	@agent
	def chief_marketing_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['chief_marketing_strategist'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False,
		)

	@agent
	def creative_content_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['creative_content_creator'],
			verbose=True,
			memory=False,
		)

	@agent
	def llm_call_session(self) -> Agent:
		return Agent(
			config=self.agents_config['llm_call_session'],
			tools=[get_current_weather],
			verbose=True,
			memory=False,
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.lead_market_analyst()
		)

	@task
	def project_understanding_task(self) -> Task:
		return Task(
			config=self.tasks_config['project_understanding_task'],
			agent=self.chief_marketing_strategist()
		)

	@task
	def marketing_strategy_task(self) -> Task:
		return Task(
			config=self.tasks_config['marketing_strategy_task'],
			agent=self.chief_marketing_strategist(),
			output_json=MarketStrategy
		)

	@task
	def campaign_idea_task(self) -> Task:
		return Task(
			config=self.tasks_config['campaign_idea_task'],
			agent=self.creative_content_creator(),
   		output_json=CampaignIdea
		)

	@task
	def copy_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['copy_creation_task'],
			agent=self.creative_content_creator(),
   		context=[self.marketing_strategy_task(), self.campaign_idea_task()],
			output_json=Copy
		)

	@task
	def weather_inquiry(self) -> Task:
		return Task(
			config=self.tasks_config['weather_inquiry'],
			agent=self.llm_call_session(),
			output_json=WeatherReport
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the MarketingPosts crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
