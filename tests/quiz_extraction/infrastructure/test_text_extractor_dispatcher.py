import pytest

from src.quiz_extraction.infrastructure.text_extractors.text_extractor_dispatcher import (
    TextExtractorDispatcher,
    UnsupportedFileFormatError,
)


def test_dispatcher_raises_for_unsupported_extension() -> None:
    dispatcher = TextExtractorDispatcher()

    with pytest.raises(UnsupportedFileFormatError):
        dispatcher.extract(b"cualquier contenido", "archivo.txt")


def test_dispatcher_detects_extension_case_insensitive() -> None:
    dispatcher = TextExtractorDispatcher()

    with pytest.raises(UnsupportedFileFormatError):
        dispatcher.extract(b"x", "archivo.RTF")
