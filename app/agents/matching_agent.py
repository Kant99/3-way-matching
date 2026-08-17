import os

from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from app.capabilities.matching_tools import (
    calculate_line_amount,
    run_3_way_matching,
)


load_dotenv()


def create_matching_agent() -> Agent:
    """
    Create the primary 3-way matching orchestration agent.
    """

    base_url = os.getenv("FOUNDRY_OPENAI_BASE_URL")
    api_key = os.getenv("FOUNDRY_API_KEY")
    model = os.getenv("FOUNDRY_MODEL")

    if not base_url:
        raise RuntimeError(
            "FOUNDRY_OPENAI_BASE_URL is not configured."
        )

    if not api_key:
        raise RuntimeError(
            "FOUNDRY_API_KEY is not configured."
        )

    if not model:
        raise RuntimeError(
            "FOUNDRY_MODEL is not configured."
        )

    client = OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

    agent = Agent(
        client=client,
        name="three_way_matching_agent",
        instructions=(
            "You are the orchestration agent for a contract, "
            "purchase order, and invoice 3-way matching workflow. "
            "You coordinate deterministic Python tools, reason "
            "about exceptions, explain validation results, and "
            "route cases requiring human judgment to HITL. "
            "\n\n"
            "IMPORTANT: Never perform arithmetic yourself when "
            "a deterministic Python tool is available. "
            "Use the appropriate tool and rely on its result. "
            "\n\n"
            "The deterministic matching tool is the authoritative "
            "source for validation results. Never independently "
            "calculate, recalculate, override, or infer validation "
            "outcomes. When the tool returns exceptions, explain "
            "the returned exception types, fields, expected values, "
            "actual values, and tolerances using only the tool result."
        ),
        tools=[
            calculate_line_amount,
            run_3_way_matching
        ],
    )

    return agent