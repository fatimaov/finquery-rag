import streamlit as st
from rag import answer_baseline, answer_contextual_rewriting, rewrite_question

st.title("finQuery")


def show_retrieved_chunks(chunks: list[str]) -> None:
    """Display retrieved chunks in a consistent expandable section."""
    if chunks:
        with st.expander("Retrieved chunks"):
            for index, chunk in enumerate(chunks, start=1):
                st.caption(f"Chunk {index}")
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
    st.info(
        "HyDE (Hypothetical Document Embeddings) is a placeholder. This technique is not implemented yet."
    )

with multi_query_tab:
    st.info(
        "Multi-query retrieval with fusion search is a placeholder. This technique is not implemented yet."
    )
