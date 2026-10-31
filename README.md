# finQuery — RAG Learning Project

A simple Retrieval-Augmented Generation (RAG) application built with Python and Streamlit to practice the fundamentals of a RAG pipeline.

This project is inspired by the **Build a RAG App** lesson from Codecademy's [Retrieval-Augmented Generation for AI Applications](https://www.codecademy.com/enrolled/courses/retrieval-augmented-generation-for-ai-applications) course.

## Data Source

The preparation script downloads the [Personal Finance textbook PDF](https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf) from Saylor Academy and extracts Chapters 1, 2, 3, 5, 7, and 8. It formats the extracted content as Markdown, including chapter and section headings. Refer to the source document for its attribution and reuse terms.

## Tech Stack

- **Python 3.13** — Core application logic
- **Streamlit** — Web interface
- **ChromaDB** — Persistent vector storage, embeddings, and similarity search
- **LangChain Text Splitters** — Markdown-aware document chunking
- **LM Studio** — Local LLM inference through its OpenAI-compatible API
- **OpenAI Python SDK** — Communication with the local LLM

## Project Structure

- `prepare.py`: Downloads the PDF, extracts the selected chapters using the table of contents, and cleans and formats their text as Markdown.
- `chunk.py`: Splits the Markdown by heading and then into 800-character chunks with 100-character overlap, retaining heading metadata.
- `ingest.py`: Stores chunks in the persistent ChromaDB collection `financial_documents` in `./chroma_db`, replacing obsolete records when the selected chapter set changes.
- `rag.py`: Retrieves matching chunks from ChromaDB and sends them with the question to the configured LM Studio model.
- `app.py`: Streamlit interface for questions, retrieval-count selection, answers, and short previews of the retrieved chunks.

## Setup and Usage

### Install dependencies

This project uses Pipenv:

```bash
pip install pipenv
pipenv install
```

### Configure LM Studio

Start LM Studio's local server with a chat model loaded, then set these environment variables to match the server and model:

- `LM_STUDIO_BASE_URL`: OpenAI-compatible API base URL, such as `http://localhost:1234/v1`
- `LM_STUDIO_MODEL`: model identifier accepted by the local server

The OpenAI client uses a placeholder API key because the local LM Studio server does not require an OpenAI key.

### Prepare the vector database

Run ingestion to download and prepare the textbook, create chunks, and store them in ChromaDB:

```bash
pipenv run python ingest.py
```

### Run the app

```bash
pipenv run streamlit run app.py
```

Enter a question and choose how many matching chunks to retrieve (1–20; default 5). The answer appears with a short preview of each retrieved chunk below it.

### Check retrieval

After ingestion, you can run a semantic query that requests two matching chunks:

```bash
pipenv run python -c 'import chromadb; c=chromadb.PersistentClient("./chroma_db").get_collection("financial_documents"); r=c.query(query_texts=["How do I create a budget?"], n_results=2); print("matches:", len(r["ids"][0])); [print("\n", i+1, r["ids"][0][i], r["metadatas"][0][i], "distance:", r["distances"][0][i], "\n", r["documents"][0][i][:350]) for i in range(len(r["ids"][0]))]'
```

The output shows the matching count, each chunk's heading metadata, distance, and a text preview.

## Purpose

This is a learning exercise focused on understanding and implementing the core components of a RAG pipeline, rather than building a production-ready application.
