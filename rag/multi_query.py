"""Helpers for generating alternative search queries."""

import re

from rag.common import llm_client, lm_studio_model, retrieve_chunks

RRF_CONSTANT = 60


ALTERNATIVE_QUERY_INSTRUCTIONS = """
Create alternative search queries for a personal finance textbook.
Each query must preserve the user's original intent while using different
wording or focusing on a relevant aspect of the same question. Do not answer
the question, introduce unrelated topics, or add unsupported assumptions.
Return only the queries, one per line, without numbering or other commentary.
""".strip()


def generate_alternative_queries(question: str, count: int = 3) -> list[str]:
    """Ask the local model for distinct search queries with the same intent."""
    if count < 1:
        raise ValueError("count must be at least 1")

    response = llm_client.chat.completions.create(
        model=lm_studio_model,
        messages=[
            {"role": "system", "content": ALTERNATIVE_QUERY_INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    f"Generate {count} alternative search queries for this question:\n\n"
                    f"{question}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content or ""
    queries = []
    seen = set()
    for line in content.splitlines():
        # Accept numbered or bulleted output even though the prompt asks for plain lines.
        query = re.sub(r"^\s*(?:[-*•]\s*|\d+[.)]\s*)", "", line).strip()
        normalized = query.casefold()
        if query and normalized not in seen:
            queries.append(query)
            seen.add(normalized)
        if len(queries) == count:
            break

    return queries or [question.strip()]


def retrieve_chunks_for_queries(
    queries: list[str], top_k: int = 5
) -> dict[str, list[str]]:
    """Retrieve a ranked chunk list for each query, preserving query order."""
    return {query: retrieve_chunks(query, top_k) for query in queries}


def fuse_ranked_results(
    ranked_results: dict[str, list[str]], rrf_constant: int = RRF_CONSTANT
) -> list[tuple[str, float]]:
    """Combine query rankings with Reciprocal Rank Fusion (highest score first)."""
    if rrf_constant < 0:
        raise ValueError("rrf_constant must be zero or greater")

    scores: dict[str, float] = {}
    for chunks in ranked_results.values():
        # Ranks start at 1; missing chunks add no contribution for that query.
        seen_in_query = set()
        for rank, chunk in enumerate(chunks, start=1):
            if chunk in seen_in_query:
                continue
            seen_in_query.add(chunk)
            scores[chunk] = scores.get(chunk, 0.0) + 1 / (rrf_constant + rank)

    # Python's stable sort keeps first-seen order when scores are tied.
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def select_top_chunks(
    fused_results: list[tuple[str, float]], top_k: int = 5
) -> list[str]:
    """Return the top_k chunks from the fused ranking for the answer context."""
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    return [chunk for chunk, _score in fused_results[:top_k]]
