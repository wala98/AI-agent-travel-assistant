from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crewai import LLM


llm = LLM(
    model="gemini/gemini-2.5-flash",
    
    api_key=" ",
    
)
from pydantic import BaseModel, Field
from typing import List, Optional

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class Travel_agent_crew():
    """TravelAgent crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def travel_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_manager'],
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm, 
            tools=[], 
            reasoning=False 
          
            
        )

    @agent
    def weather_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_agent'],
            verbose=True ,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm, 
            tools=[], 
            reasoning=False 
        )

    @agent
    def transportation_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['transportation_finder'],
            verbose=True ,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm, 
            tools=[], 
            reasoning=False 
        )

    @agent
    def accommodation_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['accommodation_finder'],
            verbose=True ,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm, 
            tools=[], 
            reasoning=False 
        )

    @agent
    def destination_experience_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['destination_experience_finder'],
            verbose=True ,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm, 
            tools=[], 
            reasoning=False 
        )

    @task
    def gather_weather_info(self) -> Task:
        return Task(
            config=self.tasks_config['gather_weather_info'],
            agent=self.weather_agent(),
            markdown = True
        )

    @task
    def find_transportation(self) -> Task:
        return Task(
            config=self.tasks_config['find_transportation'],
            agent=self.transportation_finder() ,
            markdown = True
        )

    @task
    def find_accommodation(self) -> Task:
        return Task(
            config=self.tasks_config['find_accommodation'],
            agent=self.accommodation_finder() , 
            markdown = True
        )

    @task
    def find_experiences(self) -> Task:
        return Task(
            config=self.tasks_config['find_experiences'],
            agent=self.destination_experience_finder() , 
            markdown = True
        )

    @task
    def travel_manager_task(self) -> Task:
        return Task(
            config=self.tasks_config['travel_manager_task'],
            agent=self.travel_manager() ,
            markdown = True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TravelAgent crew"""
        return Crew(
            agents=[self.destination_experience_finder(),
            self.accommodation_finder(),
            self.transportation_finder(),
            self.weather_agent()],
            tasks=self.tasks,
            llm = llm,
            process=Process.hierarchical,
            manager_agent=self.travel_manager(),
            function_calling_llm=llm, 
            verbose=True,
            planning=True ,
            planning_llm = llm 

        )
