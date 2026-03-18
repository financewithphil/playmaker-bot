from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.embeddings import embed_query
from app.config import TOP_K_RESULTS


def retrieve_relevant_chunks(db: Session, query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    query_embedding = embed_query(query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    result = db.execute(
        text("""
            SELECT content, document_name, chunk_index,
                   1 - (embedding <=> :embedding::vector) as similarity
            FROM document_chunks
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {"embedding": embedding_str, "limit": top_k},
    )

    chunks = []
    for row in result:
        chunks.append(
            {
                "content": row.content,
                "document_name": row.document_name,
                "chunk_index": row.chunk_index,
                "similarity": float(row.similarity),
            }
        )
    return chunks
