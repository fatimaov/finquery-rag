"""Helpers for contextual query rewriting."""

from rag.common import (
    build_prompt,
    generate_answer,
    llm_client,
    lm_studio_model,
    retrieve_chunks,
)


REWRITE_INSTRUCTIONS = """
Rewrite the latest user message as one concise, standalone search query for a
personal finance textbook.

Use prior turns to resolve references and recover the topic when the latest
message is a follow-up. Use assistant turns only as clues to the conversation's
topic. When the user changes topics, follow the new topic. Preserve the user's
intent, names, amounts, and constraints. Use precise textbook terminology when
it expresses the same meaning (for example, "expenses exceed income" can be
phrased as "budget deficit").

Keep the output focused on the user's information need. Return exactly one
search query, with no answer, explanation, or extra text.
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
            "content": (
                "Rewrite the latest user message as a standalone search query.\n"
                f"<latest_message>\n{current_message}\n</latest_message>"
            ),
        }
    )

    response = llm_client.chat.completions.create(
        model=lm_studio_model,
        messages=messages,
    )
    
    return (response.choices[0].message.content or "").strip()


def answer_contextual_rewriting(
    question: str, top_k: int = 5
) -> tuple[str, list[str]]:
    """Retrieve and answer using the self-contained question."""
    chunks = retrieve_chunks(question, top_k)
    if not chunks:
        return "I couldn't find relevant information in the available documents.", []

    prompt = build_prompt(question, chunks)
    return generate_answer(prompt), chunks
