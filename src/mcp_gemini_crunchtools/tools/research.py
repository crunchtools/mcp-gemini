"""Deep research tools."""

import time
from typing import Any

from ..client import get_client

# In-memory research operation store
_research_ops: dict[str, dict[str, Any]] = {}


async def gemini_deep_research(
    query: str,
) -> dict[str, Any]:
    """Start a deep research task.

    Deep research uses a specialized Gemini model that performs
    multi-step web research to answer complex questions.

    Args:
        query: The research question or topic.

    Returns:
        Research operation ID for status checking.
    """
    client = get_client()

    response = client.generate_content(
        model="gemini-1.5-pro-latest",  # Using stable versioned model
        contents=[query],
    )

    op_id = f"research-{int(time.time())}"
    _research_ops[op_id] = {
        "query": query,
        "response": response,
        "started": time.time(),
    }

    return {
        "research_id": op_id,
        "status": "complete",
        "response": response.text if response else None,
        "query": query,
    }


async def gemini_check_research(
    research_id: str,
) -> dict[str, Any]:
    """Check the status of a deep research operation.

    Args:
        research_id: The research ID from gemini_deep_research.

    Returns:
        Research status and results if complete.
    """
    if research_id not in _research_ops:
        return {"research_id": research_id, "status": "not_found"}

    op = _research_ops[research_id]
    response = op["response"]

    return {
        "research_id": research_id,
        "status": "complete",
        "response": response.text if response else None,
        "query": op["query"],
    }


async def gemini_research_followup(
    research_id: str,
    question: str,
) -> dict[str, Any]:
    """Ask a follow-up question about completed research.

    Args:
        research_id: The research ID from a previous research operation.
        question: Follow-up question.

    Returns:
        Follow-up response.
    """
    if research_id not in _research_ops:
        return {"research_id": research_id, "status": "not_found"}

    op = _research_ops[research_id]
    client = get_client()

    original_response = op["response"].text if op["response"] else ""
    prompt = (
        f"Based on this research:\n\n{original_response}\n\n"
        f"Answer this follow-up question: {question}"
    )

    response = client.generate_content(
        model="gemini-1.5-flash-latest",
        contents=[prompt],
    )

    return {
        "research_id": research_id,
        "response": response.text,
        "question": question,
    }
