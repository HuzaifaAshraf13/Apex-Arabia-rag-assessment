
---

# Apex AI Arabia - Healthcare Patient-Service Assistant API

## 📋 Project Overview

A production-ready FastAPI healthcare assistant built for Saudi enterprise standards, featuring automated appointment tools, secure RAG policy grounding, and prompt-injection defense.

---

## What Works vs. What's Next

### ✅ What Works

* **FastAPI Backend & Pydantic Validation:** Strongly typed request/response contracts ensuring predictable API behavior.
* **Local RAG Retrieval:** TF-IDF keyword retriever extracting hospital policies (fasting, ECG prep, Saudi insurance networks, and cancellation guidelines) with con
fidence scoring.
* **Tool Orchestration:** End-to-end support for availability checks, appointment booking, lookups, rescheduling, cancellations, and human escalation.
* **Security Guardrails:** Instant detection and blocking of prompt-injection attempts and unauthorized system overrides.

### ⚠️ Known Limitations

* **Stateless History:** Conversation history is accepted in the payload, but multi-turn pronoun resolution is not yet fully parsed.
* **Synchronous Tools:** Tool execution is synchronous; downstream timeouts rely on basic error handling rather than circuit breakers.

### 🚀 Future Roadmap

* **Vector Database:** Migrate to ChromaDB with `sentence-transformers` for deep semantic search.
* **Stateful Sessions:** Integrate Redis for multi-turn session and conversation tracking.
* **Resilience:** Add retry logic and circuit breakers for external clinic API calls.

---

## ⚙️ Setup & Execution

1. **Install dependencies:**
```bash
pip install -r requirements.txt

```

**1. Run locally (development):**
```bash
uvicorn main:app --reload --port 8000
```

**2. Build the Docker image:**
```bash
sudo docker build -t my-rag .
```

**3. Run the application in Docker:**
```bash
sudo docker run -d --name rag-api -p 8000:8000 my-rag
```

**4. Access the API:**

Open http://localhost:8000/docs in your browser.

3. **Test the endpoint:** Access the interactive Swagger UI documentation at `http://localhost:8000/docs`.
4. **Run automated tests:**
```bash
pytest

```



---

## 🔌 API Example & Live Verification

### Request (cURL)

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/assistant/message' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "patient_id": "PAT123",
  "message": "can you check my appointment status?",
  "conversation_history": []
}'

```

### Server Response (`200 OK`)

```json
{
  "response_message": "Found your appointment: ID APT-9876 for Cardiology 
  on 2026-04-15 at 10:00 AM (Status: confirmed).",
  "intent": "lookup",
  "requires_human_escalation": false,
  "tool_calls_executed": [
    "lookup_appointment"
  ],
  "rag_source_grounding": null
}

```

---

## 💡 Bonus Judgment Challenge — Senior Leadership Directive

**Instruction Challenged:** A senior leader proposes deploying a fully autonomous agentic loop with write-access to the live clinic database to handle bookings, cancellations, and complex modifications without human validation to maximize speed.

* **What I Would Accept:** Deploying retrieval-augmented generation (RAG) and read-only lookup/availability workflows autonomously to reduce wait times.
* **What I Would Change:** Any write operation (such as bookings, cancellations, or rescheduling) must require strict deterministic validation schemas or human care coordinator sign-off.
* **Why:** In Saudi healthcare enterprise contexts, autonomous agent loops carry a high risk of hallucinating tool arguments, overriding patient data incorrectly, or violating compliance policies.
---

## 🤖 AI & Tools Disclosure

* **Tools Used:** Gemini (for architectural brainstorming, boilerplate generation, and edge-case structuring).
* **What Was Accelerated:** Rapid drafting of FastAPI schemas, test harness setup, and structuring enterprise documentation.
* **Independent Verification:** All business logic, RAG confidence scoring, tool validation constraints, and security guardrails were manually reviewed, tested via `pytest`, and verified to align with Apex AI Arabia standards.