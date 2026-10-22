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

    # Read existing IDs only, then select the records managed by this Chapter 1
    # ingestion pipeline. The prefix keeps other collection records untouched.
    chapter_chunk_prefix = "chapter-1-chunk-"
    existing_chapter_ids = [
        chunk_id
        for chunk_id in collection.get(include=[])["ids"]
        if chunk_id.startswith(chapter_chunk_prefix)
    ]

    # Assign a repeatable ID to each current chunk so rerunning ingestion updates
    # existing records instead of creating duplicates.
    chunk_ids = [
        f"{chapter_chunk_prefix}{index}"
        for index in range(len(chunks))
    ]

    if chunks:
        # Chroma embeds each document when embeddings are not supplied and stores
        # the associated heading metadata alongside each chunk.
        collection.upsert(
            ids=chunk_ids,
            documents=[chunk.page_content for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
        )

    # Remove IDs from an earlier run that are not present in the current chunk
    # set. This also clears old Chapter 1 records when no chunks are produced.
    obsolete_ids = sorted(set(existing_chapter_ids) - set(chunk_ids))
    if obsolete_ids:
        collection.delete(ids=obsolete_ids)

    # If there are no current chunks, finish after cleaning up any old records.
    if not chunks:
        print(f"No chunks were generated; removed {len(obsolete_ids)} old Chapter 1 records.")
        return 0

    # Report how many chunks this run wrote and the collection's total record
    # count, which may include records from other sources or chapters.
    stored_count = collection.count()
    print(
        f"Stored {len(chunks)} Chapter 1 chunks and removed "
        f"{len(obsolete_ids)} obsolete records. Collection now has "
        f"{stored_count} records."
    )
    return len(chunks)


if __name__ == "__main__":
    # Run the ingestion pipeline when this file is executed as a script.
    ingest_chapter()
