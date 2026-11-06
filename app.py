import streamlit as st
from rag import answer_baseline

st.title("finQuery")

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
            if chunks:
                st.divider()

            for index, chunk in enumerate(chunks, start=1):
                preview = chunk[:300].strip()
                if len(chunk) > 300:
                    preview += "…"
                st.caption(f"Chunk {index}")
                st.markdown(
                    f'<p style="color: #777">{preview}</p>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Please enter a question.")

with rewriting_tab:
    st.info("Contextual Query Rewriting is a placeholder. This technique is not implemented yet.")

with hyde_tab:
    st.info("HyDE (Hypothetical Document Embeddings) is a placeholder. This technique is not implemented yet.")

with multi_query_tab:
    st.info("Multi-query retrieval with fusion search is a placeholder. This technique is not implemented yet.")
