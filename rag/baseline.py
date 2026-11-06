from rag.common import build_prompt, collection, generate_answer

# Exclude retrieved chunks whose ChromaDB distance exceeds this cutoff.
MAX_DISTANCE = 0.8


def retrieve_chunks(question: str, top_k: int = 5) -> list[str]:
    """Return up to top_k matching chunks that meet the distance cutoff."""
    # ChromaDB embeds the question and returns up to top_k nearest documents.
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
    )

    # This query has one result group; pair each document with its distance.
    documents = results["documents"][0] or []
    distances = results["distances"][0] or []
    return [
        document
        for document, distance in zip(documents, distances)
        if distance <= MAX_DISTANCE
    ]


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
