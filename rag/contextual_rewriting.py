"""Helpers for contextual query rewriting."""

from rag.common import build_prompt, generate_answer, llm_client, lm_studio_model
from rag.baseline import retrieve_chunks


REWRITE_INSTRUCTIONS = """
Turn the latest user message into one concise, standalone search query for the
personal finance textbook. Use recent conversation to identify the ongoing
topic. If the latest message continues that topic, include the missing subject
or concept in the query, even if the message is otherwise understandable. Use
assistant replies only to identify the topic, never to repeat or summarize
their answer. Follow a clear change of subject. Preserve names, amounts, and
intent; use precise textbook terms when supported (for example, "expenses exceed
income" means "budget deficit"). Do not add assumptions or answer the question.
Return only the query.
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
            "content": f"Rewrite this latest message as a concise standalone search query:\n\n{current_message}",
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
