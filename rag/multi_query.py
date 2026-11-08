"""Helpers for generating alternative search queries."""

import re

from rag.common import llm_client, lm_studio_model


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
