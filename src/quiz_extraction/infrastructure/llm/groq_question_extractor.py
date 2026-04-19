import json
import logging
import time
from pathlib import Path

from groq import Groq

from src.config import Settings
from src.quiz_extraction.application.ports.question_extractor_port import QuestionExtractorPort
from src.quiz_extraction.domain.question import Question, QuestionAlternative, QuestionType
from src.quiz_extraction.domain.quiz_result import QuizResult


logger = logging.getLogger(__name__)


class QuestionExtractionError(RuntimeError):
    pass

_PROMPT_PATH = Path(__file__).parent / "prompts" / "quiz_extraction.md"
SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

class GroqQuestionExtractor(QuestionExtractorPort):
    def __init__(self, settings: Settings) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model
        self._temperature = settings.groq_temperature
        self._max_tokens = settings.groq_max_tokens

    def extract(self, text: str) -> QuizResult:
        if not text.strip():
            logger.warning("llm.extract.empty_text_skipped")
            return QuizResult(total_questions=0, questions=[])

        start = time.perf_counter()
        logger.info(
            "llm.extract.started model=%s input_chars=%d",
            self._model, len(text),
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        except Exception as exc:
            logger.error("llm.extract.api_failed error=%s", exc)
            raise QuestionExtractionError(
                f"Error al llamar al LLM: {exc}"
            ) from exc

        duration_ms = int((time.perf_counter() - start) * 1000)
        raw_json = response.choices[0].message.content or "{}"

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.error(
                "llm.extract.invalid_json duration_ms=%d error=%s",
                duration_ms, exc,
            )
            raise QuestionExtractionError(
                f"El LLM devolvió un JSON inválido: {exc}"
            ) from exc

        result = self._to_quiz_result(data)
        logger.info(
            "llm.extract.completed model=%s questions=%d duration_ms=%d",
            self._model, result.total_questions, duration_ms,
        )
        return result

    def _to_quiz_result(self, data: dict) -> QuizResult:
        raw_questions = data.get("questions", [])
        questions = [self._to_question(q) for q in raw_questions]
        return QuizResult(
            total_questions=data.get("total_questions", len(questions)),
            questions=questions,
        )

    def _to_question(self, data: dict) -> Question:
        alternatives = [
            QuestionAlternative(letter=a["letter"], text=a["text"])
            for a in data.get("alternatives", [])
        ]
        return Question(
            number=int(data["number"]),
            content=data["content"],
            type=QuestionType(data["type"]),
            alternatives=alternatives,
            correct_answer=data.get("correct_answer"),
        )