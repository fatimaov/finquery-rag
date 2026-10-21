# finQuery — RAG Learning Project

A simple Retrieval-Augmented Generation (RAG) application built with Python and Streamlit to practice the fundamentals of a RAG pipeline.

This project is inspired by the **Build a RAG App** lesson from Codecademy's [Retrieval-Augmented Generation for AI Applications](https://www.codecademy.com/enrolled/courses/retrieval-augmented-generation-for-ai-applications) course.

## Data Source

The preparation script downloads the [Personal Finance textbook PDF](https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf) from Saylor Academy and extracts Chapter 1. The extracted text is intended as source material for the RAG application.

Refer to the source document for its attribution and reuse terms.

## Tech Stack
- **Python** — Core application logic
- **Streamlit** — Web interface
- **ChromaDB** — Vector storage, embeddings, and similarity search
- **LangChain Text Splitters** — Document chunking
- **LM Studio** — Local LLM inference
- **OpenAI Python SDK** — Communication with the local LLM

## Project Structure

- `prepare.py`: Load the PDF, clean its content, and structure the text as Markdown.
- `chunk.py`: Split the prepared Markdown into chunks and preserve chapter and section metadata.
- `ingest.py`: Generate embeddings and store the chunks in the persistent ChromaDB collection `financial_documents`.
- `rag.py`: Retrieve relevant chunks from ChromaDB, build the context-aware prompt, and generate an answer using the local LLM through LM Studio.
- `app.py`: Provide a simple Streamlit interface for submitting questions and displaying generated answers.

## Setup and Usage

### Install dependencies

This project targets Python 3.13 and uses Pipenv to manage its dependencies:

```bash
pip install pipenv
pipenv install
```

### Prepare the vector database

Run the preparation script when you first create the database or need to refresh its contents:

```bash
pipenv run python prepare.py
```

### Start the app

```bash
pipenv run start
```

## Purpose

This is a learning exercise focused on understanding and implementing the core components of a RAG pipeline, rather than building a production-ready application.
