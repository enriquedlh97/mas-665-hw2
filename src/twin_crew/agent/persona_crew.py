from collections.abc import Callable
from pathlib import Path

import yaml
from crewai import Agent, Crew, Task
from langchain_anthropic import ChatAnthropic

from twin_crew.config import settings


def create_persona_handler() -> Callable[[str], str]:
    config_path = Path(__file__).parent.parent / "config"
    with open(config_path / "agents.yaml") as f:
        agents_config = yaml.safe_load(f)
    with open(config_path / "tasks.yaml") as f:
        tasks_config = yaml.safe_load(f)

    agent_config = agents_config["chat_manager"]
    persona_agent = Agent(
        role=agent_config["role"],
        goal=agent_config["goal"],
        backstory=agent_config["backstory"],
        verbose=settings.debug_mode,
        allow_delegation=False,
        llm=ChatAnthropic(
            api_key=settings.anthropic_api_key, model=settings.claude_model
        ),
    )

    task_config = tasks_config["greet_and_explain_purpose"]

    def handle_message(message_text: str) -> str:
        try:
            formatted_description = task_config["description"].format(
                user_input=message_text
            )

            persona_task = Task(
                description=formatted_description,
                expected_output=task_config["expected_output"],
                agent=persona_agent,
            )

            crew = Crew(
                agents=[persona_agent],
                tasks=[persona_task],
                verbose=settings.debug_mode,
            )

            result = crew.kickoff()
            return str(result).strip()
        except Exception as e:
            return f"An error occurred: {e}"

    return handle_message
