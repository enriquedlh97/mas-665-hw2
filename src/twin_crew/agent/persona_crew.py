from collections.abc import Callable
from typing import Any, Final

from crewai import Crew, Process, Task
from crewai.crews.crew_output import CrewOutput
from crewai.project import CrewBase, agent, crew, task
from langchain_anthropic import ChatAnthropic

from twin_crew.agent.named_agent import NamedAgent
from twin_crew.config import settings


@CrewBase
class PersonaCrew:
    agents_config: Final[str] = "src/twin_crew/config/agents.yaml"
    tasks_config: Final[str] = "src/twin_crew/config/tasks.yaml"

    @agent  # type: ignore
    def persona_agent(self) -> NamedAgent:
        config: dict[str, Any] = self.agents_config["chat_manager"]  # type: ignore
        return NamedAgent(
            name=config["name"],
            config=config,
            verbose=settings.debug_mode,
            allow_delegation=False,
            llm=ChatAnthropic(
                api_key=settings.anthropic_api_key, model=settings.claude_model
            ),
        )

    @task  # type: ignore
    def persona_task(self) -> Task:
        return Task(
            config=self.tasks_config["greet_and_explain_purpose"],  # type: ignore
            # agent=self.persona_agent(),
        )

    @crew  # type: ignore
    def crew(self) -> Crew:
        return Crew(
            agents=[self.persona_agent()],
            tasks=[self.persona_task()],
            process=Process.sequential,
            verbose=settings.debug_mode,
        )


def create_persona_handler() -> Callable[[str], str]:
    persona_crew_instance = PersonaCrew()

    def handle_message(message_text: str) -> str:
        try:
            inputs: dict[str, str] = {"user_input": message_text}
            result: CrewOutput = persona_crew_instance.crew().kickoff(inputs=inputs)
            return str(result)
        except Exception as e:
            return f"An error occurred: {e}"

    return handle_message
