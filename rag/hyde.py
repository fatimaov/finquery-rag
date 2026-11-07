"""Helpers for Hypothetical Document Embeddings (HyDE)."""

from rag.common import llm_client, lm_studio_model


HYPOTHETICAL_ANSWER_INSTRUCTIONS = """
Write a short, plausible answer to the user's personal finance question that
could appear in a financial education textbook. Focus on relevant concepts and
terms that may help find useful reference material. Do not mention that the
answer is hypothetical, do not cite sources, and do not add meta commentary.
""".strip()


def generate_hypothetical_answer(question: str) -> str:
    """Ask the configured model for hypothetical text to use during retrieval."""
    response = llm_client.chat.completions.create(
        model=lm_studio_model,
        messages=[
            {"role": "system", "content": HYPOTHETICAL_ANSWER_INSTRUCTIONS},
            {"role": "user", "content": question},
        ],
    )

    # This text is only a retrieval aid; the final answer will use real chunks.
    return (response.choices[0].message.content or "").strip()
