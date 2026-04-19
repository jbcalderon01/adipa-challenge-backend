import io

from docx import Document

from src.quiz_extraction.application.ports.text_extractor_port import TextExtractorPort


class DocxTextExtractor(TextExtractorPort):
    def extract(self, file_bytes: bytes, filename: str) -> str:
        document = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()