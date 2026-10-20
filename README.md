# finQuery — RAG Learning Project

A simple Retrieval-Augmented Generation (RAG) application built with Python and Streamlit to practice the fundamentals of a RAG pipeline.

This project is inspired by the **Build a RAG App** lesson from Codecademy's [Retrieval-Augmented Generation for AI Applications](https://www.codecademy.com/enrolled/courses/retrieval-augmented-generation-for-ai-applications) course.

## Data Source

The application uses the freely accessible online textbook [A Plain Language Guide to Personal Financial Planning](https://pressbooks.salemstate.edu/personalfinance/) as its knowledge source.

The goal is to retrieve relevant information from the book and use it to generate context-aware answers to users' questions.

### Data attribution

This project uses material from **A Plain Language Guide to Personal Financial Planning** by Miranda Lam (© 2025), published by Salem State University. [View the original book](https://pressbooks.salemstate.edu/personalfinance/). The book's published license is [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/).

## Tech Stack

- **Python** — Core application logic
- **Streamlit** — Web interface
- **ChromaDB** — Vector storage, embeddings, and similarity search
- **LangChain Text Splitters** — Document chunking
- **LM Studio** — Local LLM inference
- **OpenAI Python SDK** — Communication with the local LLM

## Project Structure

- `prepare.py`: Run separately whenever you want to populate or update the vector database.
- `rag.py`: Retrieve relevant chunks from the existing ChromaDB collection and send them to LM Studio.
- `app.py`: Display a question input and the generated answer using Streamlit.

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
