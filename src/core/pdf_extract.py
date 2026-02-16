from __future__ import annotations

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes, max_chars: int = 60_000) -> str:
    """
    Extract raw text from a PDF (good-enough extraction for this project).
    Caps output to avoid huge prompts.
    """
    reader = PdfReader(io_bytes := _bytes_to_filelike(file_bytes))
    parts: list[str] = []

    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            parts.append(txt)

    text = "\n\n".join(parts).strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TRUNCATED]"
    return text


def _bytes_to_filelike(b: bytes):
    import io

    return io.BytesIO(b)
