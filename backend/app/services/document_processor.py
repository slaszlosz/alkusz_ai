import os
from typing import List, Dict, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
import tiktoken


class DocumentProcessor:
    """Process and chunk documents for vector storage"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def process_pdf(self, file_path: str) -> Tuple[List[Dict], int]:
        """
        Extract text from PDF and chunk it
        Returns: (chunks, page_count)
        """
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        chunks = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                page_chunks = self._chunk_text(text, page_num)
                chunks.extend(page_chunks)

        return chunks, page_count

    def process_docx(self, file_path: str) -> Tuple[List[Dict], int]:
        """
        Extract text from DOCX and chunk it
        Returns: (chunks, page_count estimate)
        """
        doc = DocxDocument(file_path)
        full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        # Estimate page count (rough: 500 words per page)
        word_count = len(full_text.split())
        page_count = max(1, word_count // 500)

        chunks = self._chunk_text(full_text, page=1)
        return chunks, page_count

    def process_txt(self, file_path: str) -> Tuple[List[Dict], int]:
        """
        Extract text from TXT and chunk it
        Returns: (chunks, page_count estimate)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Estimate page count
        word_count = len(text.split())
        page_count = max(1, word_count // 500)

        chunks = self._chunk_text(text, page=1)
        return chunks, page_count

    def _chunk_text(self, text: str, page: int) -> List[Dict]:
        """
        Split text into chunks with overlap
        """
        tokens = self.encoding.encode(text)
        chunks = []

        start = 0
        chunk_index = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append({
                "text": chunk_text,
                "page": page,
                "chunk_index": chunk_index
            })

            chunk_index += 1
            start = end - self.chunk_overlap

        return chunks

    def process_document(self, file_path: str, filename: str) -> Tuple[List[Dict], int]:
        """
        Process document based on file extension
        Returns: (chunks, page_count)
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.pdf':
            return self.process_pdf(file_path)
        elif ext == '.docx':
            return self.process_docx(file_path)
        elif ext == '.txt':
            return self.process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
