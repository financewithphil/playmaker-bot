import anthropic
from app.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT
from app.services.retriever import retrieve_relevant_chunks
from sqlalchemy.orm import Session

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant documents found."

    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[From: {chunk['document_name']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(context_parts)


def chat(db: Session, user_message: str, conversation_history: list[dict]) -> str:
    chunks = retrieve_relevant_chunks(db, user_message)
    context = build_context(chunks)

    augmented_message = f"""Here is relevant context from Matty's documented playbooks:

{context}

---

User's question: {user_message}"""

    messages = []
    for msg in conversation_history[-10:]:  # Keep last 10 messages for context
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": augmented_message})

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text
