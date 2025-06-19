import io
from typing import Optional
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(file_content: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file_content: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_content))
    text = "\n".join([p.text for p in doc.paragraphs])
    return text.strip()

def extract_cv_text(file_content: bytes, extension: str) -> Optional[str]:
    extension = extension.lower()
    if extension == "pdf":
        return extract_text_from_pdf(file_content)
    elif extension == "docx":
        return extract_text_from_docx(file_content)
    elif extension == "doc":
        # Optional: Use textract, but it requires external dependencies
        return "DOC file format not supported in this implementation."
    return None
