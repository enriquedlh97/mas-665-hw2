from collections.abc import Callable

from nanda_adapter import NANDA

from twin_crew.agent.sarcastic_crew import create_sarcastic_handler
from twin_crew.config import settings


def main() -> None:
    try:
        sarcastic_logic: Callable[[str], str] = create_sarcastic_handler()
        nanda = NANDA(sarcastic_logic)

        print("Starting Sarcastic Agent with CrewAI...")
        print("All messages will be transformed to sarcastic responses!")

        nanda.start_server_api(
            anthropic_key=settings.anthropic_api_key,
            domain=settings.domain_name,
            port=settings.agent_port,
            public_url=settings.public_url,
            ssl=settings.ssl_enabled,
        )

    except Exception as e:
        raise RuntimeError(f"Failed to start sarcastic agent: {e}") from e


if __name__ == "__main__":
    main()
