from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import os
import shutil
from app.db.database import get_db
from app.db.models import Document
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.core.config import get_settings

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a document"""

    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create document record
    doc = Document(
        filename=file.filename,
        file_path="",  # Will be set after saving
        mime_type=file.content_type,
        category=category
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Save file
    file_path = os.path.join(settings.upload_dir, f"{doc.id}_{file.filename}")
    doc.file_path = file_path

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        doc.file_size = os.path.getsize(file_path)

        # Process document
        processor = DocumentProcessor()
        chunks, page_count = processor.process_document(file_path, file.filename)

        doc.page_count = page_count
        doc.chunk_count = len(chunks)

        # Add to vector store
        vector_store = VectorStore()
        vector_store.add_document_chunks(
            doc_id=doc.id,
            filename=file.filename,
            chunks=chunks,
            category=category
        )

        doc.processed = True
        await db.commit()
        await db.refresh(doc)

        return {
            "id": doc.id,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "chunk_count": doc.chunk_count,
            "category": doc.category,
            "processed": doc.processed
        }

    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        await db.delete(doc)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all documents"""
    result = await db.execute(
        select(Document).order_by(Document.upload_date.desc())
    )
    documents = result.scalars().all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_size": doc.file_size,
            "page_count": doc.page_count,
            "chunk_count": doc.chunk_count,
            "category": doc.category,
            "upload_date": doc.upload_date.isoformat(),
            "processed": doc.processed
        }
        for doc in documents
    ]


@router.get("/{doc_id}")
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Get document details"""
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_size": doc.file_size,
        "page_count": doc.page_count,
        "chunk_count": doc.chunk_count,
        "category": doc.category,
        "upload_date": doc.upload_date.isoformat(),
        "processed": doc.processed
    }


@router.get("/{doc_id}/download")
async def download_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Download document file"""
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type=doc.mime_type
    )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    vector_store = VectorStore()
    vector_store.delete_document(doc_id)

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from database
    await db.delete(doc)
    await db.commit()

    return {"message": "Document deleted successfully"}


@router.get("/stats/overview")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics"""
    result = await db.execute(select(Document))
    documents = result.scalars().all()

    vector_store = VectorStore()
    vector_stats = vector_store.get_stats()

    return {
        "total_documents": len(documents),
        "processed_documents": sum(1 for doc in documents if doc.processed),
        "total_pages": sum(doc.page_count or 0 for doc in documents),
        "total_chunks": vector_stats["total_chunks"]
    }
