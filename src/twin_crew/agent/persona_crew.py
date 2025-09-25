from collections.abc import Callable

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from twin_crew.config import settings


@CrewBase
class PersonaCrew:
    agents_config = "src/twin_crew/config/agents.yaml"
    tasks_config = "src/twin_crew/config/tasks.yaml"

    @agent  # type: ignore
    def chat_manager(self) -> Agent:
        config = self.agents_config["chat_manager"]  # type: ignore
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=settings.debug_mode,
            allow_delegation=False,
            llm=settings.claude_model,
        )

    @task  # type: ignore
    def greet_and_explain_purpose(self) -> Task:
        return Task(
            config=self.tasks_config["greet_and_explain_purpose"],  # type: ignore
        )

    @crew  # type: ignore
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # type: ignore
            tasks=self.tasks,  # type: ignore
            process=Process.sequential,
            verbose=settings.debug_mode,
        )


def create_persona_handler() -> Callable[[str], str]:
    persona_crew_instance = PersonaCrew()

    def handle_message(message_text: str) -> str:
        try:
            inputs = {"user_input": message_text}
            result = persona_crew_instance.crew().kickoff(inputs=inputs)
            return str(result).strip()
        except Exception as e:
            return f"An error occurred: {e}"

    return handle_message
