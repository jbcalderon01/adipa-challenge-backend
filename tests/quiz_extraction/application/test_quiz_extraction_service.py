import pytest

from src.quiz_extraction.application.ports.question_extractor_port import QuestionExtractorPort
from src.quiz_extraction.application.ports.text_extractor_port import TextExtractorPort
from src.quiz_extraction.application.services.quiz_extraction_service import (
    NoQuestionsFoundError,
    QuizExtractionService,
)
from src.quiz_extraction.domain.question import Question, QuestionType
from src.quiz_extraction.domain.quiz_result import QuizResult


class FakeTextExtractor(TextExtractorPort):
    def __init__(self, text: str) -> None:
        self._text = text

    def extract(self, file_bytes: bytes, filename: str) -> str:
        return self._text


class FakeQuestionExtractor(QuestionExtractorPort):
    def __init__(self, result: QuizResult) -> None:
        self._result = result

    def extract(self, text: str) -> QuizResult:
        return self._result


def _sample_result(n_questions: int) -> QuizResult:
    questions = [
        Question(number=i, content=f"Pregunta {i}", type=QuestionType.OPEN_ENDED)
        for i in range(1, n_questions + 1)
    ]
    return QuizResult(total_questions=n_questions, questions=questions)


def test_extract_returns_result_when_questions_are_found() -> None:
    service = QuizExtractionService(
        text_extractor=FakeTextExtractor("texto del documento"),
        question_extractor=FakeQuestionExtractor(_sample_result(2)),
    )

    result = service.extract(b"fake-bytes", "examen.pdf")

    assert result.total_questions == 2
    assert len(result.questions) == 2


def test_extract_raises_no_questions_found_when_result_is_empty() -> None:
    service = QuizExtractionService(
        text_extractor=FakeTextExtractor("documento sin preguntas"),
        question_extractor=FakeQuestionExtractor(_sample_result(0)),
    )

    with pytest.raises(NoQuestionsFoundError):
        service.extract(b"fake-bytes", "recibo.pdf")


def test_extract_propagates_text_extractor_errors() -> None:
    class FailingExtractor(TextExtractorPort):
        def extract(self, file_bytes: bytes, filename: str) -> str:
            raise ValueError("boom")

    service = QuizExtractionService(
        text_extractor=FailingExtractor(),
        question_extractor=FakeQuestionExtractor(_sample_result(1)),
    )

    with pytest.raises(ValueError, match="boom"):
        service.extract(b"fake-bytes", "algo.pdf")
