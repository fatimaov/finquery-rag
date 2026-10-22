from chunk import chunk_chapter
import chromadb

# Open the persistent database directory so ingested records remain available
# after the script exits and can be reused by the RAG application.
client = chromadb.PersistentClient("./chroma_db")

# Reuse this collection on later runs, creating it on the first ingestion run.
collection = client.get_or_create_collection(name="financial_documents")


def ingest_chapter():
    """Create Chapter 1 chunks and store them in the persistent collection."""
    # Prepare Chapter 1 and split it into metadata-aware text chunks.
    chunks = chunk_chapter()

    # Leave the collection unchanged when the source produces no chunks.
    if not chunks:
        print("No chunks were generated; the collection was not changed.")
        return 0

    # Give each chunk a repeatable ID so rerunning ingestion updates the same
    # records instead of creating duplicates. Chroma embeds each document when
    # embeddings are not supplied and stores the associated heading metadata.
    collection.upsert(
        ids=[f"chapter-1-chunk-{index}" for index in range(len(chunks))],
        documents=[chunk.page_content for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
    )

    # Report how many chunks this run wrote and the collection's total record
    # count, which may include records from other sources or chapters.
    stored_count = collection.count()
    print(f"Stored {len(chunks)} Chapter 1 chunks. Collection now has {stored_count} records.")
    return len(chunks)


if __name__ == "__main__":
    # Run the ingestion pipeline when this file is executed as a script.
    ingest_chapter()
