from pathlib import Path

from src.quiz_extraction.application.ports.text_extractor_port import TextExtractorPort
from src.quiz_extraction.infrastructure.text_extractors.docx_text_extractor import DocxTextExtractor
from src.quiz_extraction.infrastructure.text_extractors.pdf_text_extractor import PdfTextExtractor
from src.quiz_extraction.infrastructure.text_extractors.xlsx_text_extractor import XlsxTextExtractor


class UnsupportedFileFormatError(ValueError):
    pass


class TextExtractorDispatcher(TextExtractorPort):
    def __init__(self) -> None:
        self._extractors: dict[str, TextExtractorPort] = {
            ".pdf": PdfTextExtractor(),
            ".docx": DocxTextExtractor(),
            ".xlsx": XlsxTextExtractor(),
        }

    def extract(self, file_bytes: bytes, filename: str) -> str:
        extension = Path(filename).suffix.lower()
        extractor = self._extractors.get(extension)
        if extractor is None:
            raise UnsupportedFileFormatError(
                f"Formato no soportado: {extension}. Usa .pdf, .docx o .xlsx."
            )
        return extractor.extract(file_bytes, filename)