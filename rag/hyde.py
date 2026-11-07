"""Helpers for Hypothetical Document Embeddings (HyDE)."""

from rag.common import (
    build_prompt,
    generate_answer,
    llm_client,
    lm_studio_model,
    retrieve_chunks,
)


HYPOTHETICAL_ANSWER_INSTRUCTIONS = """
Write one short, keyword-rich sentence of hypothetical textbook-style text
related to the user's personal finance question. Prioritize the main topic,
relevant financial concepts, and useful terminology or synonyms that may help
retrieve reference material. Do not try to fully resolve the question, mention
that the text is hypothetical, cite sources, or add meta commentary. Return
only the hypothetical sentence.
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


def retrieve_hypothetical_chunks(
    hypothetical_answer: str, top_k: int = 5
) -> list[str]:
    """Retrieve real document chunks using the hypothetical answer as the query."""
    # Shared retrieval applies the collection settings and MAX_DISTANCE cutoff.
    return retrieve_chunks(hypothetical_answer, top_k)


def generate_hyde_answer(question: str, chunks: list[str]) -> str:
    """Generate a grounded answer using real chunks and the original question."""
    prompt = build_prompt(question, chunks)
    return generate_answer(prompt)


def answer_with_hyde(
    question: str, hypothetical_answer: str, top_k: int = 5
) -> tuple[str, list[str]]:
    """Return a grounded answer and its chunks using pre-generated HyDE text."""
    chunks = retrieve_hypothetical_chunks(hypothetical_answer, top_k)

    # Do not ask the model to answer from an empty context.
    if not chunks:
        return (
            "I couldn't find relevant information in the available documents.",
            [],
        )

    answer = generate_hyde_answer(question, chunks)
    return answer, chunks
