from collections.abc import Callable

from crewai import Agent, Crew, Task
from langchain_anthropic import ChatAnthropic

from twin_crew.config import settings


def create_sarcastic_handler() -> Callable[[str], str]:
    llm = ChatAnthropic(api_key=settings.anthropic_api_key, model=settings.claude_model)

    sarcastic_agent = Agent(
        role="Sarcastic Message Transformer",
        goal="Transform messages into witty, sarcastic responses while maintaining the core meaning",
        backstory="""You are a master of sarcasm and wit. You excel at taking ordinary messages
        and transforming them into clever, sarcastic versions that are humorous but not mean-spirited.
        You use techniques like irony, exaggeration, and dry humor to make messages more entertaining.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    def sarcastic_improvement(message_text: str) -> str:
        try:
            sarcastic_task = Task(
                description=f"""Transform the following message into a sarcastic, witty version.
                Use sarcasm, irony, and dry humor while keeping the core meaning intact.
                Make it entertaining but not offensive or mean-spirited.

                Original message: {message_text}

                Provide only the sarcastic transformation, no explanations.""",
                expected_output="A sarcastic, witty version of the original message",
                agent=sarcastic_agent,
            )

            crew = Crew(agents=[sarcastic_agent], tasks=[sarcastic_task], verbose=True)

            result = crew.kickoff()
            return str(result).strip()

        except Exception as e:
            raise RuntimeError(
                f"Failed to process sarcastic transformation: {e}"
            ) from e

    return sarcastic_improvement
