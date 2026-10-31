import streamlit as st
from rag import answer_question

st.title("finQuery")
st.write("Ask questions about personal finance.")

question = st.text_input("Your question")
top_k = st.number_input(
    "Number of chunks to retrieve",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
)

if st.button("Ask"):
    if question.strip():
        with st.spinner("Generating answer..."):
            answer, chunks = answer_question(question, top_k=int(top_k))

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
