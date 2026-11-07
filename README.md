# finQuery — RAG Learning Project

A Retrieval-Augmented Generation (RAG) learning app built with Python and Streamlit. It demonstrates baseline retrieval, contextual query rewriting, and Hypothetical Document Embeddings (HyDE). Multi-Query + Fusion is a placeholder.

This project is inspired by the **Build a RAG App** lesson from Codecademy's [Retrieval-Augmented Generation for AI Applications](https://www.codecademy.com/enrolled/courses/retrieval-augmented-generation-for-ai-applications) course.

## Demo

<img src="demo.gif" alt="finQuery app demo" width="1200">

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
- `app.py`: Streamlit interface with tabs for Baseline RAG, Contextual Query Rewriting, HyDE, and Multi-Query + Fusion.
- `rag/`: Retrieval pipelines and shared RAG components:
  - `common.py`: Shared ChromaDB and LM Studio clients, chunk retrieval, prompt construction, and answer generation.
  - `baseline.py`: Baseline RAG answer generation using shared retrieval.
  - `contextual_rewriting.py`: Rewrites follow-up questions using chat history, then uses shared retrieval to generate an answer.
  - `hyde.py`: Generates a short hypothetical text for retrieval, then answers using matching real chunks.
  - `multi_query.py`: Placeholder for multi-query retrieval and fusion search.
  - `__init__.py`: Exposes the implemented pipeline entry points from the `rag` package.

The Contextual Query Rewriting tab shows the conversation in a scrollable chat history and keeps the message box at the bottom. It rewrites a question only when earlier messages exist. Chat history is stored in Streamlit session state and lasts for the active session.

## Setup and Usage

### Install dependencies

This project uses Pipenv:

```bash
pip install pipenv
pipenv install
```

### Configure LM Studio

Start LM Studio's local server with a chat model loaded, then set the environment variables shown in `.env.example` to match the server and model:

- `LM_STUDIO_BASE_URL`: OpenAI-compatible API base URL, such as `http://localhost:1234/v1`
- `LM_STUDIO_MODEL`: model identifier accepted by the local server
- `LM_STUDIO_API_KEY`: API key passed to the OpenAI-compatible client; LM Studio commonly accepts a placeholder such as `lm-studio` for local use.

`.env.example` is a template; the app reads these values from the process environment. Set them in your shell or your preferred environment-variable manager before running ingestion or the app. Do not commit real credentials.

### Prepare the vector database

Run ingestion to download and prepare the textbook, create chunks, and store them in ChromaDB:

```bash
pipenv run python ingest.py
```

### Run the app

```bash
pipenv run streamlit run app.py
```

In Baseline RAG, enter a question and choose how many chunks to retrieve (1–20; default 5). In Contextual Query Rewriting, submit a message in the chat box; follow-up questions use earlier turns as context. In HyDE, the app shows the generated hypothetical sentence, searches with it, and uses the original question plus retrieved chunks to generate a grounded answer. These tabs show retrieved chunks in an expander. Retrieval excludes chunks whose ChromaDB distance is greater than `0.8`, so fewer chunks than requested may be shown. If no chunks pass the cutoff, the app displays a fallback message.

### Check retrieval

After ingestion, you can run a semantic query that requests two matching chunks:

```bash
pipenv run python -c 'import chromadb; c=chromadb.PersistentClient("./chroma_db").get_collection("financial_documents"); r=c.query(query_texts=["How do I create a budget?"], n_results=2); print("matches:", len(r["ids"][0])); [print("\n", i+1, r["ids"][0][i], r["metadatas"][0][i], "distance:", r["distances"][0][i], "\n", r["documents"][0][i][:350]) for i in range(len(r["ids"][0]))]'
```

The output shows the matching count, each chunk's heading metadata, distance, and a text preview.

## Purpose

This is a learning exercise focused on understanding and implementing the core components of a RAG pipeline, rather than building a production-ready application.
