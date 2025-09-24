import json
import platform
import re
import sys
import threading
import time
from datetime import datetime
from typing import Any

import click
from crewai import Crew
from crewai.llm import LLM
from crewai.types.crew_chat import ChatInputField, ChatInputs
from crewai.utilities.llm_utils import create_llm

from twin_crew.named_agent import NamedAgent


def run_custom_chat(
    crew_instance: Crew, manager_agent: NamedAgent | None = None
) -> None:
    """
    Generic interactive chat that mirrors crewAI's chat behavior while
    allowing a manager persona and manager-defined LLM when provided.
    """
    chat_llm: LLM | None = initialize_chat_llm(crew_instance, manager_agent)
    if not chat_llm:
        return

    # Analyze crew to produce dynamic inputs and tool schema
    loading_complete = threading.Event()
    loading_thread = threading.Thread(target=show_loading, args=(loading_complete,))
    loading_thread.start()

    try:
        crew_name: str = crew_instance.__class__.__name__
        chat_inputs: ChatInputs = generate_crew_chat_inputs(
            crew_instance, crew_name, chat_llm
        )
        tool_schema: dict = generate_crew_tool_schema(chat_inputs)
        system_message: str = build_system_message(chat_inputs, manager_agent)
        introductory_message: str = chat_llm.call(
            messages=[{"role": "system", "content": system_message}]
        )
    finally:
        loading_complete.set()
        loading_thread.join()

    # Announce intro in persona voice if available
    speaker_label: str = get_agent_display_name(manager_agent)
    click.secho(f"\n{speaker_label}: {introductory_message}\n", fg="green")

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    # Expose a single callable tool = the crew itself (generic)
    available_functions: dict[str, Any] = {
        chat_inputs.crew_name: create_tool_function(crew_instance, messages),
    }

    chat_loop(chat_llm, messages, tool_schema, available_functions, speaker_label)


def initialize_chat_llm(crew: Crew, manager_agent: NamedAgent | None) -> LLM | None:
    """
    Initialize LLM with priority:
    1) manager_agent.llm if provided
    2) crew.chat_llm if set
    3) default "gpt-4o"
    """
    try:
        if manager_agent and getattr(manager_agent, "llm", None):
            return create_llm(manager_agent.llm)
        if getattr(crew, "chat_llm", None):
            return create_llm(crew.chat_llm)
        return create_llm("gpt-4o")
    except Exception as e:
        click.secho(f"Unable to initialize chat LLM: {e}", fg="red")
        return None


def show_loading(event: threading.Event) -> None:
    """Display animated loading dots while processing."""
    click.secho(
        "\nAnalyzing crew and required inputs - this may take a few seconds depending on complexity.",
        fg="white",
    )
    while not event.is_set():
        print(".", end="", flush=True)
        time.sleep(1)
    print()


def build_system_message(
    chat_inputs: ChatInputs, manager_agent: NamedAgent | None
) -> str:
    """
    Persona-first system message if a manager is provided; otherwise neutral,
    but always includes dynamic crew name, description, and required inputs.
    """
    required_fields_str: str = (
        ", ".join(
            f"{field.name} (desc: {field.description or 'n/a'})"
            for field in chat_inputs.inputs
        )
        or "(No required fields detected)"
    )

    if manager_agent:
        return (
            f"You are {manager_agent.role}. "
            f"Your name: {manager_agent.name}. Always introduce yourself by name so people know who you are."
            f"Your goal: {manager_agent.goal}. "
            f"Backstory: {manager_agent.backstory}\n\n"
            "You assist users with this crew's purpose. "
            "You have a single function (tool) you can call by name once you have all required inputs. "
            f"Those required inputs are: {required_fields_str}. "
            "Before calling any function, first reply by indicating to the user that you will call the function (crew, crew function or however you want to call it), "
            "and ask the user to confirm if that is fine. Only after the user confirm can you call the function."
            "IMPORTANT: When calling the crew function, you must automatically include your own professional background as 'enrique_background' parameter. "
            "Write a detailed summary of your background (education, experience, current interests in AI/agentic systems, etc.) to help the crew understand who you are. Try to write a t least 200 words for this."
            "Do NOT show this background summary to the user - it should only be passed internally to the crew."
            "Keep responses concise and friendly. If the user drifts off-topic, provide a brief answer and guide them back to the crew's purpose.\n"
            f"Crew Name: {chat_inputs.crew_name}\n"
            f"Crew Description: {chat_inputs.crew_description}"
        )

    return (
        "You are a helpful AI assistant for the CrewAI platform. "
        "Your primary purpose is to assist users with the crew's specific tasks. "
        "You can answer general questions, but should guide users back to the crew's purpose afterward. "
        "You have a single function (tool) you can call by name once you have all required inputs. "
        f"Those required inputs are: {required_fields_str}. "
        "Before calling any function, first reply by indicating to the user that you will call the function (crew, crew function or however you want to call it), "
        "and ask the user to confirm if that is fine. Only after the user confirm can you call the function."
        "When you have them, call the function. Keep responses concise and friendly. "
        "If a user asks a question outside the crew's scope, provide a brief answer and remind them of the crew's purpose.\n"
        f"Crew Name: {chat_inputs.crew_name}\n"
        f"Crew Description: {chat_inputs.crew_description}"
    )


def create_tool_function(crew: Crew, messages: list[dict[str, str]]) -> Any:
    """Create a wrapper that runs the crew with the chat transcript included."""

    def run_with_messages(**kwargs: Any) -> str:
        # Hidden pre-call note so the model can remember a tool call started
        start_time = datetime.now().isoformat(timespec="seconds")
        messages.append(
            {
                "role": "system",
                "content": f"[state] About to call crew '{crew.__class__.__name__}' at {start_time}. Next assistant message (message I send) will be the output received.",
            }
        )

        result_str = run_crew_tool(crew, messages, **kwargs)
        # Hidden persistent memory for the model about tool usage
        run_time = datetime.now().isoformat(timespec="seconds")
        messages.append(
            {
                "role": "system",
                "content": f"[state] Crew '{crew.__class__.__name__}' was called successfully at {run_time}.",
            }
        )
        # Return raw result string; the assistant will acknowledge then display this content
        return result_str

    return run_with_messages


def run_crew_tool(crew: Crew, messages: list[dict[str, str]], **kwargs: Any) -> str:
    """
    Runs the crew using crew.kickoff(inputs=kwargs) and returns the output as string.
    Mirrors original behavior and includes serialized chat messages for context.
    """
    try:
        kwargs["crew_chat_messages"] = json.dumps(messages)
        crew_output = crew.kickoff(inputs=kwargs)
        return str(crew_output)
    except Exception as e:
        click.secho("An error occurred while running the crew:", fg="red")
        click.secho(str(e), fg="red")
        sys.exit(1)


def chat_loop(
    chat_llm: LLM,
    messages: list[dict[str, str]],
    crew_tool_schema: dict[str, Any],
    available_functions: dict[str, Any],
    speaker_label: str,
) -> None:
    """Main chat loop for interacting with the user."""
    while True:
        try:
            flush_input()
            user_input: str = get_user_input()
            handle_user_input(
                user_input,
                chat_llm,
                messages,
                crew_tool_schema,
                available_functions,
                speaker_label,
            )
        except KeyboardInterrupt:
            click.echo("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            click.secho(f"An error occurred: {e}", fg="red")
            break


def get_user_input() -> str:
    """Collect multi-line user input with exit handling."""
    click.secho(
        "\nYou (type your message below. Press 'Enter' twice when you're done, or type 'exit' to quit):",
        fg="blue",
    )
    user_input_lines: list[str] = []
    while True:
        line: str = input()
        if line.strip().lower() == "exit":
            return "exit"
        if line == "":
            break
        user_input_lines.append(line)
    return "\n".join(user_input_lines)


def handle_user_input(
    user_input: str,
    chat_llm: LLM,
    messages: list[dict[str, str]],
    crew_tool_schema: dict[str, Any],
    available_functions: dict[str, Any],
    speaker_label: str,
) -> None:
    """Handle user input and generate assistant response."""
    if user_input.strip().lower() == "exit":
        click.echo("Exiting chat. Goodbye!")
        return

    if not user_input.strip():
        click.echo("Empty message. Please provide input or type 'exit' to quit.")
        return

    messages.append({"role": "user", "content": user_input})

    click.echo()
    click.secho(f"{speaker_label} is thinking... 🤔", fg="cyan")

    final_response = chat_llm.call(
        messages=messages,
        tools=[crew_tool_schema],
        available_functions=available_functions,
    )

    # If a tool was just called (tool wrapper appends a state note), present the crew output via a system-instructed formatter
    if (
        messages
        and messages[-1].get("role") == "system"
        and isinstance(messages[-1].get("content"), str)
        and messages[-1]["content"].startswith("[state] Crew ")
        and "was called successfully" in messages[-1]["content"]
    ):
        crew_output = final_response

        presenter_system_message = (
            "You just received the crew's final output. This is an internal system message and the user will not see it. "
            "Craft a message for the user that presents the crew's output. Keep the output of the crew exactly as is."
        )

        formatted_response = chat_llm.call(
            messages=messages
            + [
                {
                    "role": "system",
                    "content": f"{presenter_system_message}\n\n[crew_output]\n{crew_output}",
                }
            ]
        )

        messages.append({"role": "assistant", "content": formatted_response})
        click.secho(f"\n{speaker_label}: {formatted_response}\n", fg="green")
        return

    messages.append({"role": "assistant", "content": final_response})
    click.secho(f"\n{speaker_label}: {final_response}\n", fg="green")


def flush_input() -> None:
    """Flush any pending input from the user."""
    if platform.system() == "Windows":
        import msvcrt

        while msvcrt.kbhit():  # type: ignore
            msvcrt.getch()  # type: ignore
    else:
        import termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)


# ---------- Dynamic crew analysis (ported from original) ----------


def get_agent_display_name(manager_agent: NamedAgent | None) -> str:
    """Extract the agent name for chat labels."""
    if not manager_agent:
        return "Assistant"
    return manager_agent.name


def generate_crew_chat_inputs(crew: Crew, crew_name: str, chat_llm: LLM) -> ChatInputs:
    """Analyze the crew to construct ChatInputs containing name, description, and input fields."""
    required_inputs: set[str] = fetch_required_inputs(crew)

    input_fields: list[ChatInputField] = []
    for input_name in required_inputs:
        description = generate_input_description_with_ai(input_name, crew, chat_llm)
        input_fields.append(ChatInputField(name=input_name, description=description))

    crew_description: str = generate_crew_description_with_ai(crew, chat_llm)
    return ChatInputs(
        crew_name=crew_name, crew_description=crew_description, inputs=input_fields
    )


def fetch_required_inputs(crew: Crew) -> set[str]:
    """Extract placeholders from the crew's tasks and agents, e.g., {brain_dump}."""
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    required_inputs: set[str] = set()

    for task in crew.tasks:
        text = f"{task.description or ''} {task.expected_output or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    for agent in crew.agents:
        text = f"{agent.role or ''} {agent.goal or ''} {agent.backstory or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    return required_inputs


def generate_input_description_with_ai(
    input_name: str, crew: Crew, chat_llm: LLM
) -> str:
    """Generate a concise input description using AI based on crew context (same behavior as original)."""
    context_texts: list[str] = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in crew.tasks:
        if f"{{{input_name}}}" in (task.description or "") or f"{{{input_name}}}" in (
            task.expected_output or ""
        ):
            task_description = placeholder_pattern.sub(
                lambda m: m.group(1), task.description or ""
            )
            expected_output = placeholder_pattern.sub(
                lambda m: m.group(1), task.expected_output or ""
            )
            context_texts.append(f"Task Description: {task_description}")
            context_texts.append(f"Expected Output: {expected_output}")

    for agent in crew.agents:
        if (
            f"{{{input_name}}}" in (agent.role or "")
            or f"{{{input_name}}}" in (agent.goal or "")
            or f"{{{input_name}}}" in (agent.backstory or "")
        ):
            agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
            agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
            agent_backstory = placeholder_pattern.sub(
                lambda m: m.group(1), agent.backstory or ""
            )
            context_texts.append(f"Agent Role: {agent_role}")
            context_texts.append(f"Agent Goal: {agent_goal}")
            context_texts.append(f"Agent Backstory: {agent_backstory}")

    context: str = "\n".join(context_texts)
    if not context:
        raise ValueError(f"No context found for input '{input_name}'.")

    prompt: str = (
        f"Based on the following context, write a concise description (15 words or less) of the input '{input_name}'.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response: str = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip()


def generate_crew_description_with_ai(crew: Crew, chat_llm: LLM) -> str:
    """Generate a short crew description from tasks and agents (same behavior as original)."""
    context_texts: list[str] = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in crew.tasks:
        task_description = placeholder_pattern.sub(
            lambda m: m.group(1), task.description or ""
        )
        expected_output = placeholder_pattern.sub(
            lambda m: m.group(1), task.expected_output or ""
        )
        context_texts.append(f"Task Description: {task_description}")
        context_texts.append(f"Expected Output: {expected_output}")

    for agent in crew.agents:
        agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
        agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
        agent_backstory = placeholder_pattern.sub(
            lambda m: m.group(1), agent.backstory or ""
        )
        context_texts.append(f"Agent Role: {agent_role}")
        context_texts.append(f"Agent Goal: {agent_goal}")
        context_texts.append(f"Agent Backstory: {agent_backstory}")

    context: str = "\n".join(context_texts)
    if not context:
        raise ValueError("No context found for generating crew description.")

    prompt: str = (
        "Based on the following context, write a concise, action-oriented description (15 words or less) of the crew's purpose.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response: str = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip()


def generate_crew_tool_schema(crew_inputs: ChatInputs) -> dict:
    """Build Littellm 'function' schema for the crew (same shape as original)."""
    properties: dict[str, Any] = {}
    for field in crew_inputs.inputs:
        properties[field.name] = {
            "type": "string",
            "description": field.description or "No description provided",
        }

    required_fields: list[str] = [field.name for field in crew_inputs.inputs]

    return {
        "type": "function",
        "function": {
            "name": crew_inputs.crew_name,
            "description": crew_inputs.crew_description or "No crew description",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_fields,
            },
        },
    }
