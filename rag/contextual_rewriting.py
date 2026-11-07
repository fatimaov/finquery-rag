"""Helpers for contextual query rewriting."""

from rag.common import llm_client, lm_studio_model


REWRITE_INSTRUCTIONS = """
Rewrite the user's latest message as a self-contained question that can be
understood without seeing the conversation history. Use the history only to
resolve references and omitted context. Preserve the user's intent and do not
answer the question. Return only the rewritten question. If the latest message
is already self-contained, return it unchanged.
""".strip()


def rewrite_question(
    history: list[dict[str, str]], current_message: str
) -> str:
    """Rewrite the current message using prior turns as context."""
    messages = [{"role": "system", "content": REWRITE_INSTRUCTIONS}]

    # Add only prior user and assistant turns; the new message stays separate.
    messages.extend(
        {"role": message["role"], "content": message["content"]}
        for message in history
        if message.get("role") in {"user", "assistant"}
    )
    messages.append(
        {
            "role": "user",
            "content": f"Rewrite this latest message as a self-contained question:\n\n{current_message}",
        }
    )

    response = llm_client.chat.completions.create(
        model=lm_studio_model,
        messages=messages,
    )
    
    return (response.choices[0].message.content or "").strip()
