from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.config import Settings, get_settings
from src.quiz_extraction.application.services.quiz_extraction_service import (
    NoQuestionsFoundError,
    QuizExtractionService,
)
from src.quiz_extraction.infrastructure.llm.groq_question_extractor import (
    GroqQuestionExtractor,
    QuestionExtractionError,
)
from src.quiz_extraction.infrastructure.text_extractors.text_extractor_dispatcher import (
    TextExtractorDispatcher,
    UnsupportedFileFormatError,
)
from src.quiz_extraction.presentation.dtos.quiz_dtos import QuizResultDTO


router = APIRouter(prefix="/quiz", tags=["quiz"])


def get_quiz_extraction_service(
    settings: Settings = Depends(get_settings),
) -> QuizExtractionService:
    return QuizExtractionService(
        text_extractor=TextExtractorDispatcher(),
        question_extractor=GroqQuestionExtractor(settings),
    )


@router.post(
    "/extract",
    response_model=QuizResultDTO,
    response_model_by_alias=True,
)
async def extract_quiz(
    file: UploadFile = File(...),
    service: QuizExtractionService = Depends(get_quiz_extraction_service),
) -> QuizResultDTO:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre.",
        )

    file_bytes = await file.read()

    try:
        result = service.extract(file_bytes, file.filename)
    except UnsupportedFileFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except NoQuestionsFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except QuestionExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error procesando con el LLM: {exc}",
        ) from exc

    return QuizResultDTO.from_domain(result)