# src/travel_agent/crew.py
import os
import sys
from dotenv import load_dotenv, find_dotenv

# If you really need this path hack, keep it; otherwise pip -e . makes it unnecessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from tools.custom_tool import get_weather

# Load env and tune LiteLLM/Groq behavior
load_dotenv(find_dotenv())
os.environ.setdefault("LITELLM_BASE_URL", "https://api.groq.com/openai/v1")
os.environ.setdefault("LITELLM_MAX_RETRIES", "2")

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY", ""),
    temperature=0.0,
    max_tokens=256,   # was 128 — give room for final line
    num_retries=0,
)
@CrewBase
class Travel_agent_crew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def travel_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_manager'],
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm,
            tools=[get_weather],
            reasoning=False,
            verbose=False,
            max_iter=1,      # <-- CrewAI uses max_iter (not max_iterations)
            memory=False,
        )

    @task
    def travel_manager_task(self) -> Task:
        return Task(
            config=self.tasks_config['travel_manager_task'],
            agent=self.travel_manager(),
            markdown=True,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.travel_manager()],
            tasks=[self.travel_manager_task()],
            llm=llm,
            process=Process.sequential,
            manager_agent=self.travel_manager(),
            function_calling_llm=llm,
            verbose=True,
            planning=False,
        )