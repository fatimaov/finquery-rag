# finQuery — RAG Learning Project

A simple Retrieval-Augmented Generation (RAG) application built with Python and Streamlit to practice the fundamentals of a RAG pipeline.

This project is inspired by the **Build a RAG App** lesson from Codecademy's [Retrieval-Augmented Generation for AI Applications](https://www.codecademy.com/enrolled/courses/retrieval-augmented-generation-for-ai-applications) course.

## Data Source

The preparation script downloads the [Personal Finance textbook PDF](https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf) from Saylor Academy and extracts Chapters 1, 2, 3, 5, 7, and 8. The extracted text is intended as source material for the RAG application.

Refer to the source document for its attribution and reuse terms.

## Tech Stack
- **Python** — Core application logic
- **Streamlit** — Web interface
- **ChromaDB** — Vector storage, embeddings, and similarity search
- **LangChain Text Splitters** — Document chunking
- **LM Studio** — Local LLM inference
- **OpenAI Python SDK** — Communication with the local LLM

## Project Structure

- `prepare.py`: Download the PDF, use its table of contents to find selected chapters, extract and clean their text, and structure headings, paragraphs, and lists as Markdown. This demonstrates PDF text extraction and preprocessing for a RAG pipeline.
- `chunk.py`: Split the selected chapters into 800-character chunks with 100-character overlap, preserving the Markdown heading hierarchy as metadata.
- `ingest.py`: Store the chunks in the persistent ChromaDB collection `financial_documents`, removing records that are not part of the current selected-chapter set.
- `rag.py` and `app.py`: Reserved for the RAG query logic and Streamlit interface; these are not implemented yet.

## Setup and Usage

### Install dependencies

This project targets Python 3.13 and uses Pipenv to manage its dependencies:

```bash
pip install pipenv
pipenv install
```

### Prepare the vector database

Run the ingestion script to prepare the selected chapters, create their chunks, and store them in ChromaDB:

```bash
pipenv run python ingest.py
```

### Check retrieval

After ingestion, run a semantic query that requests two matching chunks:

```bash
pipenv run python -c 'import chromadb; c=chromadb.PersistentClient("./chroma_db").get_collection("financial_documents"); r=c.query(query_texts=["How do I create a budget?"], n_results=2); print("matches:", len(r["ids"][0])); [print("\n", i+1, r["ids"][0][i], r["metadatas"][0][i], "distance:", r["distances"][0][i], "\n", r["documents"][0][i][:350]) for i in range(len(r["ids"][0]))]'
```

The output should show two matches, including each chunk's heading metadata and a text preview.

### App status

The Streamlit interface and RAG query logic are not implemented yet.

## Purpose

This is a learning exercise focused on understanding and implementing the core components of a RAG pipeline, rather than building a production-ready application.
