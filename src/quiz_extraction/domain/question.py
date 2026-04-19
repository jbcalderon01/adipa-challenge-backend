from dataclasses import dataclass, field
from enum import Enum

class QuestionType(str, Enum): 
    MULTIPLE_CHOICE = "seleccion_multiple"
    TRUE_FALSE = "verdadero_falso"
    OPEN_ENDED = "desarrollo"
    MATCHING = "emparejamiento"

@dataclass(frozen=True)
class QuestionAlternative:
    letter: str
    text: str

@dataclass(frozen=True)
class Question:
    number: int
    content: str
    type: QuestionType
    alternatives: list[QuestionAlternative] = field(default_factory=list)
    correct_answer: str | None = None
