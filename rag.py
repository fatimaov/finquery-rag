import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="financial_documents")

def retrieve_chunks(question: str, top_k: int = 5):
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    return results
