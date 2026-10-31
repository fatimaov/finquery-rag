import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="financial_documents")

def retrieve_chunks(question: str, top_k: int = 5):
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    return results

def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)

    prompt = f"""
You are a financial education assistant.

Answer the user's question using only the provided context.
If the context is insufficient, say so.
Do not invent information.
Keep your answer clear and concise.

<context>
{context}
</context>

<question>
{question}
</question>
"""
    return prompt.strip()
