import json

from src.quiz_extraction.domain.question import Question, QuestionAlternative, QuestionType
from src.quiz_extraction.domain.quiz_result import QuizResult
from src.quiz_extraction.presentation.dtos.quiz_dtos import QuizResultDTO


def test_dto_serializes_with_spanish_aliases() -> None:
    domain_result = QuizResult(
        total_questions=1,
        questions=[
            Question(
                number=1,
                content="¿Capital de Chile?",
                type=QuestionType.MULTIPLE_CHOICE,
                alternatives=[
                    QuestionAlternative(letter="A", text="Lima"),
                    QuestionAlternative(letter="B", text="Santiago"),
                ],
                correct_answer="B",
            )
        ],
    )

    dto = QuizResultDTO.from_domain(domain_result)
    payload = json.loads(dto.model_dump_json(by_alias=True))

    assert "total_preguntas" in payload
    assert "preguntas" in payload
    first = payload["preguntas"][0]
    assert first["numero"] == 1
    assert first["enunciado"] == "¿Capital de Chile?"
    assert first["tipo"] == "seleccion_multiple"
    assert first["respuesta_correcta"] == "B"
    assert first["alternativas"][0] == {"letra": "A", "texto": "Lima"}
