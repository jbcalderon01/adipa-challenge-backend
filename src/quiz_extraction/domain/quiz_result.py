from dataclasses import dataclass

from src.quiz_extraction.domain.question import Question


@dataclass(frozen=True)
class QuizResult:
    total_questions: int
    questions: list[Question]
