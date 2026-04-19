import logging
import time

from src.quiz_extraction.application.ports.question_extractor_port import QuestionExtractorPort
from src.quiz_extraction.application.ports.text_extractor_port import TextExtractorPort
from src.quiz_extraction.domain.quiz_result import QuizResult


logger = logging.getLogger(__name__)


class NoQuestionsFoundError(ValueError):
    pass


class QuizExtractionService:
    def __init__(
        self,
        text_extractor: TextExtractorPort,
        question_extractor: QuestionExtractorPort,
    ) -> None:
        self._text_extractor = text_extractor
        self._question_extractor = question_extractor

    def extract(self, file_bytes: bytes, filename: str) -> QuizResult:
        start = time.perf_counter()
        logger.info(
            "quiz.extract.started filename=%s size_bytes=%d",
            filename, len(file_bytes),
        )

        text = self._text_extractor.extract(file_bytes, filename)
        result = self._question_extractor.extract(text)

        duration_ms = int((time.perf_counter() - start) * 1000)

        if result.total_questions == 0:
            logger.warning(
                "quiz.extract.no_questions_found filename=%s duration_ms=%d",
                filename, duration_ms,
            )
            raise NoQuestionsFoundError(
                "No se detectaron preguntas en el documento."
            )

        logger.info(
            "quiz.extract.completed filename=%s questions=%d duration_ms=%d",
            filename, result.total_questions, duration_ms,
        )
        return result