# SHL Assessment Recommender API

This is a conversational AI API built to recommend SHL assessments based on a user's natural language queries. 

## Features
- **Stateless Conversational Architecture:** Keeps track of conversational context via the request payload.
- **RAG via ChromaDB:** Embeds and retrieves SHL Assessment catalog data efficiently.
- **Strict Schema Enforcement:** Adheres perfectly to the mandated JSON schema structure using LLaMA-3.3 on Groq.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Add your Groq API Key to a `.env` file (`GROQ_API_KEY="..."`)
3. Run the API: `uvicorn main:app --reload`

## Endpoints
- `GET /health` : Health check.
- `POST /chat` : Multi-turn assessment recommendation.
