from chunk import chunk_selected_chapters
import chromadb

# Open the persistent database directory so ingested records remain available
# after the script exits and can be reused by the RAG application.
client = chromadb.PersistentClient("./chroma_db")

# Reuse this collection on later runs, creating it on the first ingestion run.
collection = client.get_or_create_collection(name="financial_documents")


def get_all_collection_ids(batch_size=1000):
    """Return every ID currently stored in the collection."""
    ids = []
    offset = 0

    while True:
        batch_ids = collection.get(
            include=[],
            limit=batch_size,
            offset=offset,
        )["ids"]
        if not batch_ids:
            break
        ids.extend(batch_ids)
        offset += len(batch_ids)

    return ids


def ingest_selected_chapters():
    """Create chunks for the selected chapters and store them persistently."""
    # Prepare and split all selected chapters into metadata-aware text chunks.
    chunks = chunk_selected_chapters()
    if not chunks:
        # Preserve the existing collection if preparation unexpectedly produces
        # no content, rather than replacing valid stored data with an empty set.
        raise ValueError("No chunks were generated; the collection was not changed.")

    # Give every current chunk a stable ID so reruns replace matching records.
    chunk_prefix = "selected-chapters-chunk-"
    chunk_ids = [
        f"{chunk_prefix}{index}"
        for index in range(len(chunks))
    ]
    expected_ids = set(chunk_ids)
    batch_size = 500

    # Upsert in batches so the full prepared set is stored before any old records
    # are removed. Chroma embeds documents when embeddings are not supplied.
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=chunk_ids[start:end],
            documents=[chunk.page_content for chunk in chunks[start:end]],
            metadatas=[chunk.metadata for chunk in chunks[start:end]],
        )

    # Remove every record that is not part of this run, including legacy IDs or
    # records written by earlier versions of the ingestion pipeline.
    obsolete_ids = sorted(set(get_all_collection_ids()) - expected_ids)
    for start in range(0, len(obsolete_ids), batch_size):
        collection.delete(ids=obsolete_ids[start:start + batch_size])

    # Confirm that storage contains exactly the current chunk IDs.
    stored_ids = set(get_all_collection_ids())
    if stored_ids != expected_ids:
        missing_ids = expected_ids - stored_ids
        unexpected_ids = stored_ids - expected_ids
        raise RuntimeError(
            "Collection synchronization failed: "
            f"{len(missing_ids)} chunks are missing and "
            f"{len(unexpected_ids)} unexpected records remain."
        )

    # Report the exact number of chunks now stored in the collection.
    stored_count = collection.count()
    print(
        f"Stored {stored_count} selected-chapter chunks and removed "
        f"{len(obsolete_ids)} obsolete records."
    )
    return stored_count


if __name__ == "__main__":
    # Run the ingestion pipeline when this file is executed as a script.
    ingest_selected_chapters()
