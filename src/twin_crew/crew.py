from typing import Any, Final

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from twin_crew.named_agent import NamedAgent
from twin_crew.tools.word_counter_tool import WordCounterTool


@CrewBase
class TwinCrew:
    """Twin crew"""

    agents_config: Final[str] = "config/agents.yaml"
    tasks_config: Final[str] = "config/tasks.yaml"

    @agent  # type: ignore
    def chat_manager(self) -> NamedAgent:
        config: dict[str, Any] = self.agents_config["chat_manager"]  # type: ignore
        return NamedAgent(
            name=config["name"],
            config=config,
            verbose=False,
            allow_delegation=True,
        )

    @agent  # type: ignore
    def pitch_strategist(self) -> Agent:
        return Agent(config=self.agents_config["pitch_strategist"], verbose=True)  # type: ignore

    @agent  # type: ignore
    def pitch_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["pitch_writer"],  # type: ignore
            tools=[WordCounterTool()],
            verbose=True,
        )

    @agent  # type: ignore
    def pitch_refiner(self) -> Agent:
        return Agent(
            config=self.agents_config["pitch_refiner"],  # type: ignore
            tools=[WordCounterTool()],
            verbose=True,
        )

    @task  # type: ignore
    def develop_pitch_outline_task(self) -> Task:
        return Task(
            config=self.tasks_config["develop_pitch_outline_task"],  # type: ignore
        )

    @task  # type: ignore
    def write_pitch_draft_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_pitch_draft_task"],  # type: ignore
        )

    @task  # type: ignore
    def refine_pitch_for_fit_task(self) -> Task:
        return Task(
            config=self.tasks_config["refine_pitch_for_fit_task"],  # type: ignore
        )

    @crew  # type: ignore
    def crew(self) -> Crew:
        """Creates the Twin crew"""
        worker_agents: list[Agent] = [
            self.pitch_strategist(),
            self.pitch_writer(),
            self.pitch_refiner(),
        ]

        return Crew(
            agents=worker_agents,
            # self.agents,
            tasks=self.tasks,  # type: ignore
            process=Process.sequential,
            verbose=False,
            chat_llm="gpt-4o",
        )
