from chunk import chunk_chapter


def ingest_chapter():
    """Create the chapter chunks for the ingestion pipeline."""
    return chunk_chapter()


if __name__ == "__main__":
    ingest_chapter()
