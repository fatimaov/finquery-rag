"""Public entry points for finQuery's RAG pipelines."""

from .baseline import answer_baseline
from .contextual_rewriting import answer_contextual_rewriting, rewrite_question
from .hyde import answer_with_hyde, generate_hypothetical_answer
from .multi_query import answer_with_multi_query, answer_with_multi_query_details

__all__ = [
    "answer_baseline",
    "answer_contextual_rewriting",
    "answer_with_hyde",
    "answer_with_multi_query",
    "answer_with_multi_query_details",
    "generate_hypothetical_answer",
    "rewrite_question",
]
