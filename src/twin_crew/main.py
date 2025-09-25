from collections.abc import Callable

from nanda_adapter import NANDA

from twin_crew.agent.persona_crew import create_persona_handler
from twin_crew.config import settings


def main() -> None:
    try:
        handler_logic: Callable[[str], str] = create_persona_handler()
        nanda = NANDA(handler_logic)

        print("Starting Enrique Persona Agent with CrewAI...")

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
