from typing import Any

from crewai import Agent


class NamedAgent(Agent):
    """Agent with a guaranteed name attribute for type safety."""

    name: str

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)
