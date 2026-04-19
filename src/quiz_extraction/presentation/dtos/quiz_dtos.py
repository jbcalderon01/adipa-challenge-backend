from pydantic import BaseModel, ConfigDict, Field

from src.quiz_extraction.domain.question import QuestionType
from src.quiz_extraction.domain.quiz_result import QuizResult


class QuestionAlternativeDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    letter: str = Field(alias="letra")
    text: str = Field(alias="texto")


class QuestionDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    number: int = Field(alias="numero")
    content: str = Field(alias="enunciado")
    type: QuestionType = Field(alias="tipo")
    alternatives: list[QuestionAlternativeDTO] = Field(alias="alternativas")
    correct_answer: str | None = Field(default=None, alias="respuesta_correcta")


class QuizResultDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_questions: int = Field(alias="total_preguntas")
    questions: list[QuestionDTO] = Field(alias="preguntas")

    @classmethod
    def from_domain(cls, result: QuizResult) -> "QuizResultDTO":
        return cls(
            total_questions=result.total_questions,
            questions=[
                QuestionDTO(
                    number=q.number,
                    content=q.content,
                    type=q.type,
                    alternatives=[
                        QuestionAlternativeDTO(letter=a.letter, text=a.text)
                        for a in q.alternatives
                    ],
                    correct_answer=q.correct_answer,
                )
                for q in result.questions
            ],
        )