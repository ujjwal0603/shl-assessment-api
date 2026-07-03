# Approach Document: Conversational SHL Assessment Recommender

## 1. Design Choices & Architecture
The goal was to build a stateless conversational agent that guides users from vague intents to grounded SHL assessment recommendations, strictly adhering to a predefined schema. 

I chose **FastAPI** as the web framework due to its lightweight nature, out-of-the-box asynchronous support, and rapid performance. For the LLM orchestration, I used **LangChain** in combination with the **Groq API**. Groq was selected over local models or standard cloud providers (after evaluating rate limits) because its LPU (Language Processing Unit) inference provides near-instantaneous responses, which is critical for real-time conversational agents. The specific model used was **LLaMA-3.3-70b-versatile**, as it exhibits strong instruction-following capabilities and tool-use reliability necessary for strict JSON output schema compliance.

Because the API must be stateless, the entire conversation history is passed within every `/chat` POST request. The agent processes this history to determine if it has enough context to recommend an assessment, or if it must ask clarifying questions.

## 2. Retrieval Setup (RAG)
To ground the LLM in the specific SHL product catalog, I implemented a Retrieval-Augmented Generation (RAG) pipeline using **ChromaDB**. 

1. **Ingestion:** The 377-item JSON catalog was parsed, extracting the `name`, `description`, `job_levels_raw`, and `keys` for each assessment.
2. **Embeddings:** These fields were concatenated into rich-text documents and embedded using `sentence-transformers` (all-MiniLM-L6-v2). The embeddings were stored persistently in a local Chroma collection.
3. **Tool Integration:** I exposed a `search_catalog_tool` to the LangChain agent. When the user provides sufficient context (e.g., "I need an assessment for a mid-level Java developer"), the LLM dynamically formulates a search query, invokes the tool, and retrieves the top 10 relevant items. It then maps the catalog's `keys` to the required `test_type` schema (e.g., Personality & Behavior -> 'P').

## 3. Prompt Design
The system prompt was engineered to enforce behavioral constraints and schema compliance:
*   **Behavioral Constraints:** The prompt explicitly instructs the agent to clarify vague queries, refuse off-topic requests (e.g., legal or general hiring advice), and update shortlists dynamically mid-conversation.
*   **Schema Enforcement:** The model is strictly instructed to return *only* a raw JSON object containing `reply`, `recommendations`, and `end_of_conversation`. No markdown wrappers or additional conversational filler are permitted.
*   **Zero-Shot Extraction:** The prompt defines a heuristic for the model to extract the `test_type` dynamically based on the retrieved catalog `keys`.

## 4. Evaluation Approach & Iteration
I built a Python evaluation harness (`evaluate.py`) to systematically run the agent against the provided `GenAI_SampleConversations` traces. The script parsed the markdown traces to extract user inputs and simulated the multi-turn conversations, evaluating the agent's recall by comparing its retrieved URLs against the expected URLs in the traces.

**What Didn't Work & Improvements:**
*   **Initial API Key Quota Exhaustion:** The initial deployment attempted to use Gemini-2.0-Flash, but the provided API keys were hitting `429 Quota Exceeded` errors (limit: 0). 
    *   *Improvement:* The architecture was decoupled from Google GenAI and migrated to Groq, allowing the evaluation script to proceed.
*   **Rate Limiting during Evaluation:** Groq's free tier imposes a strict tokens-per-day limit. Because the API is stateless, appending the history and the RAG tool output for 10 full conversations exhausted the token limit rapidly during testing.
    *   *Improvement:* Implemented a `time.sleep()` backoff in the evaluation script to handle TPM (tokens-per-minute) limits. While we eventually hit the daily token cap around Trace #8, the agent demonstrated a baseline Recall of ~22.2%, proving its ability to successfully execute the RAG pipeline and structure outputs correctly in a zero-shot setting.


