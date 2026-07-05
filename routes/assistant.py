"""FastAPI routes for the AI assistant."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from config.langsmith_setup import enhanced_traceable, trace_error
from agents.coordinator import process_query
from config.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    run_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
@enhanced_traceable(
    name="Inventra Chat API",
    tags=["api", "chat", "production"],
    metadata={"version": "1.0.0", "endpoint": "/chat"},
)
async def chat_assistant(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint for the Inventra AI assistant.
    Processes user queries through the multi-agent workflow.
    """
    try:
        logger.info(
            f"API Request - Query: {request.query[:100]}... (session: {request.session_id})"
        )

        # Add request metadata for tracing
        metadata = {
            "user_agent": http_request.headers.get("user-agent"),
            "query_length": len(request.query),
            "session_id": request.session_id,
        }

        # Process the query through the multi-agent workflow
        response = process_query(request.query, session_id=request.session_id)

        logger.info(f"API Response generated (session: {request.session_id})")

        return ChatResponse(
            response=response,
            session_id=request.session_id,
            run_id="tracked_by_langsmith",  # This will be populated by LangSmith
        )

    except Exception as e:
        # Trace the error with context
        trace_error(
            e,
            {
                "endpoint": "/chat",
                "query": request.query[:200],  # Truncate for privacy
                "session_id": request.session_id,
            },
        )

        logger.error(f"Error in chat_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "inventra-assistant-api"}
