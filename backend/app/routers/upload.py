import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import UPLOAD_DIR, ADMIN_SECRET
from app.models.document import DocumentChunk, UploadedDocument
from app.services.pdf_processor import extract_text_from_pdf, chunk_text
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/api/upload", tags=["upload"])


def verify_admin(x_admin_secret: str = Header(...)):
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(verify_admin),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    existing = db.query(UploadedDocument).filter_by(filename=file.filename).first()
    if existing:
        # Delete old chunks and re-ingest
        db.query(DocumentChunk).filter_by(document_name=file.filename).delete()
        db.delete(existing)
        db.commit()

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    if not chunks:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="No text content found in PDF")

    embeddings = embed_texts(chunks)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db_chunk = DocumentChunk(
            document_name=file.filename,
            chunk_index=i,
            content=chunk,
            embedding=embedding,
        )
        db.add(db_chunk)

    doc_record = UploadedDocument(filename=file.filename, total_chunks=len(chunks))
    db.add(doc_record)
    db.commit()

    os.remove(file_path)

    return {
        "message": f"Successfully ingested '{file.filename}'",
        "chunks_created": len(chunks),
    }


@router.get("/documents")
def list_documents(db: Session = Depends(get_db), _=Depends(verify_admin)):
    docs = db.query(UploadedDocument).order_by(UploadedDocument.created_at.desc()).all()
    return [
        {
            "filename": d.filename,
            "total_chunks": d.total_chunks,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.delete("/documents/{filename}")
def delete_document(filename: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    doc = db.query(UploadedDocument).filter_by(filename=filename).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.query(DocumentChunk).filter_by(document_name=filename).delete()
    db.delete(doc)
    db.commit()
    return {"message": f"Deleted '{filename}' and all its chunks"}
