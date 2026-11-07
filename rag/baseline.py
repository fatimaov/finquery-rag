from rag.common import build_prompt, generate_answer, retrieve_chunks


def answer_baseline(question: str, top_k: int = 5) -> tuple[str, list[str]]:
    """Return an answer and the retrieved chunks used to generate it."""
    # Retrieve the nearest chunks, then stop if none meet the distance cutoff.
    chunks = retrieve_chunks(question, top_k)
    if not chunks:
        return "I couldn't find relevant information in the available documents.", []

    # Give the model the question together with the retrieved reference text.
    prompt = build_prompt(question, chunks)

    # Generate and return the response from the configured LM Studio model.
    answer = generate_answer(prompt)
    return answer, chunks
