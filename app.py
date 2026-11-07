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
    ]
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

    # Render the saved conversation.
    for message in st.session_state["rewriting_messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Collect a new message. Pipeline processing will be added in a later step.
    user_message = st.chat_input(
        "Ask a question", key="rewriting_chat_input"
    )

    if user_message:
        history = st.session_state["rewriting_messages"]
        if history:
            rewritten_question = rewrite_question(
                history=history,
                current_message=user_message,
            )
        else:
            rewritten_question = user_message
        st.caption(f"Rewritten question: {rewritten_question}")

        with st.spinner("Retrieving information and generating an answer..."):
            answer, chunks = answer_contextual_rewriting(
                rewritten_question, top_k=int(rewriting_top_k)
            )

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
