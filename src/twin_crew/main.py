#!/usr/bin/env python
import sys
import warnings

from twin_crew.crew import TwinCrew
from twin_crew.custom_chat import run_custom_chat
from twin_crew.named_agent import NamedAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run() -> None:
    """
    Run the crew.
    """
    # TODO: Revise after updates
    inputs = {
        "brain_dump": """
            I would like to write a newsletter around "why is it feels so hard to get a new AI software job or land AI clients".
            It really comes down to a few idea. They are competing the same way everyone else is by updating their linkedin bio and sending out
            hundreds of resumes to the same 100 companies that are receiving thousands of applicants which makes them a needle in the hay stack.
            They aren't opening themselves up to luck by posting their work on YouTube and LinkedIn. Software is one of the only jobs where you can
            actively demo what you're capabale of in a very public settings. Take advantage of that.
            """
    }

    try:
        TwinCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}") from e


def train() -> None:
    """
    Train the crew for a given number of iterations.
    """
    # TODO: Revise after updates
    inputs = {"topic": "AI LLMs"}
    try:
        TwinCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}") from e


def replay() -> None:
    """
    Replay the crew execution from a specific task.
    """
    # TODO: Revise after updates
    try:
        TwinCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e


def test() -> None:
    """
    Test the crew execution and returns the results.
    """
    # TODO: Revise after updates
    inputs = {"topic": "AI LLMs"}
    try:
        TwinCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}") from e


def chat() -> None:
    """
    Start interactive chat with Enrique, your AI newsletter strategy assistant.
    """
    try:
        crew_instance: TwinCrew = TwinCrew()
        # Get the manager agent
        manager_agent: NamedAgent = crew_instance.chat_manager()

        run_custom_chat(crew_instance.crew(), manager_agent)

    except Exception as e:
        raise Exception(f"An error occurred while starting chat: {e}") from e
