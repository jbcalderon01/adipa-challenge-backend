import io

import pdfplumber

from src.quiz_extraction.application.ports.text_extractor_port import TextExtractorPort


class PdfTextExtractor(TextExtractorPort):
    def extract(self, file_bytes: bytes, filename: str) -> str:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        return "\n\n".join(pages_text).strip()