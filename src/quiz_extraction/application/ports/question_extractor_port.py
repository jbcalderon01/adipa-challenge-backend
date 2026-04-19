from abc import ABC, abstractmethod

from src.quiz_extraction.domain.quiz_result import QuizResult

class QuestionExtractorPort(ABC):
    @abstractmethod
    def extract(self, text: str) -> QuizResult:
        ...
        