import streamlit as st
from rag import (
    answer_baseline,
    answer_contextual_rewriting,
    answer_with_hyde,
    answer_with_multi_query_details,
    generate_hypothetical_answer,
    rewrite_question,
)

st.title("finQuery")


def show_retrieved_chunks(chunks: list[str]) -> None:
    """Display retrieved chunks in a consistent expandable section."""
    if chunks:
        with st.expander("Retrieved chunks"):
            for index, chunk in enumerate(chunks, start=1):
                st.caption(f"Chunk {index}")
                st.write(chunk)


def show_fused_chunks(
    chunks: list[str], fused_results: list[tuple[str, float]]
) -> None:
    """Display selected chunks with their rank and Reciprocal Rank Fusion score."""
    scores = {chunk: score for chunk, score in fused_results}
    if chunks:
        with st.expander("Retrieved chunks (fusion ranking)"):
            for index, chunk in enumerate(chunks, start=1):
                st.caption(f"Rank {index} · RRF score {scores[chunk]:.4f}")
                st.write(chunk)


baseline_tab, rewriting_tab, hyde_tab, multi_query_tab = st.tabs(
    [
        "Baseline RAG",
        "Contextual Query Rewriting",
        "HyDE",
        "Multi-Query + Fusion",
    ],
    on_change="rerun",
    key="finquery_tabs",
)

with baseline_tab:
    st.write("Ask questions about personal finance using semantic retrieval.")

    question = st.text_input("Your question", key="baseline_question")
    top_k = st.number_input(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="baseline_top_k",
    )

    if st.button("Ask", key="baseline_ask"):
        if question.strip():
            with st.spinner("Generating answer..."):
                answer, chunks = answer_baseline(question, top_k=int(top_k))

            st.write(answer)
            show_retrieved_chunks(chunks)
        else:
            st.warning("Please enter a question.")

with rewriting_tab:
    st.write("Ask follow-up questions about personal finance.")

    def clear_rewriting_chat() -> None:
        """Reset the contextual rewriting conversation and its input."""
        st.session_state["rewriting_messages"] = []
        st.session_state["rewriting_chat_input"] = ""

    rewriting_top_k = st.number_input(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="rewriting_top_k",
    )

    # Keep this tab's conversation across Streamlit reruns.
    if "rewriting_messages" not in st.session_state:
        st.session_state["rewriting_messages"] = []

    st.button(
        "Clear chat",
        key="clear_rewriting_chat",
        on_click=clear_rewriting_chat,
        disabled=not st.session_state["rewriting_messages"],
    )

    # Only create the bottom-anchored input while this tab is selected.
    user_message = None
    if rewriting_tab.open:
        user_message = st.bottom.chat_input(
            "Ask a question", key="rewriting_chat_input"
        )

    # Bound the conversation height so it scrolls independently of the page.
    with st.container(height=450, border=False):
        # Render saved turns, including the chunks used for each answer.
        for message in st.session_state["rewriting_messages"]:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and message.get("rewritten_question"):
                    st.caption(f"Rewritten question: {message['rewritten_question']}")
                st.write(message["content"])
                if message["role"] == "assistant":
                    show_retrieved_chunks(message.get("chunks", []))

        if user_message:
            history = st.session_state["rewriting_messages"]
            if history:
                rewritten_question = rewrite_question(
                    history=history,
                    current_message=user_message,
                )
            else:
                rewritten_question = user_message

            with st.spinner("Retrieving information and generating an answer..."):
                answer, chunks = answer_contextual_rewriting(
                    rewritten_question, top_k=int(rewriting_top_k)
                )

            # Save the original wording for display and future contextual rewrites.
            st.session_state["rewriting_messages"].append(
                {"role": "user", "content": user_message}
            )
            st.session_state["rewriting_messages"].append(
                {
                    "role": "assistant",
                    "content": answer,
                    "chunks": chunks,
                    "rewritten_question": rewritten_question,
                }
            )

            # Display the new turn now; saved turns render from session state next rerun.
            with st.chat_message("user"):
                st.write(user_message)
            with st.chat_message("assistant"):
                st.caption(f"Rewritten question: {rewritten_question}")
                st.write(answer)
                show_retrieved_chunks(chunks)

with hyde_tab:
    st.write("Ask questions about personal finance using hypothetical-answer retrieval.")

    hyde_question = st.text_input("Your question", key="hyde_question")
    hyde_top_k = st.number_input(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="hyde_top_k",
    )

    if st.button("Ask", key="hyde_ask"):
        if hyde_question.strip():
            with st.spinner("Generating hypothetical answer..."):
                hypothetical_answer = generate_hypothetical_answer(hyde_question)

            st.caption(f"Hypothetical answer used for retrieval: {hypothetical_answer}")

            with st.spinner("Retrieving information and generating an answer..."):
                answer, chunks = answer_with_hyde(
                    hyde_question,
                    hypothetical_answer,
                    top_k=int(hyde_top_k),
                )

            st.write(answer)
            show_retrieved_chunks(chunks)
        else:
            st.warning("Please enter a question.")

with multi_query_tab:
    st.write(
        "Alternative phrasings can find relevant text that a single search may miss. "
        "Reciprocal Rank Fusion combines the search rankings, giving more weight to "
        "chunks that rank highly across queries."
    )

    multi_query_question = st.text_input("Your question", key="multi_query_question")
    multi_query_top_k = st.number_input(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="multi_query_top_k",
    )

    if st.button("Ask", key="multi_query_ask"):
        if multi_query_question.strip():
            with st.spinner(
                "Generating search queries, retrieving, and fusing results..."
            ):
                answer, chunks, queries, fused_results = answer_with_multi_query_details(
                    multi_query_question,
                    top_k=int(multi_query_top_k),
                )

            with st.expander("Generated search queries"):
                for index, query in enumerate(queries, start=1):
                    st.caption(f"Query {index}: {query}")

            st.write(answer)
            show_fused_chunks(chunks, fused_results)
        else:
            st.warning("Please enter a question.")
