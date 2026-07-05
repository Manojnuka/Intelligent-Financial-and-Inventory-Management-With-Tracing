"""LangSmith tracing configuration and setup."""

import os
from typing import Optional
from functools import wraps
from langsmith import Client, traceable
from langsmith.run_helpers import trace
from config.settings import get_settings
from config.logger import get_logger

logger = get_logger(__name__)


def initialize_langsmith() -> Optional[Client]:
    """Initialize LangSmith tracing with proper configuration.

    Returns:
        LangSmith client if successfully initialized, None otherwise.
    """
    try:
        settings = get_settings()

        if not settings.langsmith_tracing:
            logger.info("LangSmith tracing is disabled")
            return None

        if not settings.langsmith_api_key:
            logger.warning("LangSmith API key not found, tracing disabled")
            return None

        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGSMITH_ENVIRONMENT"] = settings.langsmith_environment

        # Initialize client
        client = Client(
            api_url=settings.langsmith_endpoint, api_key=settings.langsmith_api_key
        )

        # Test connection
        try:
            client.list_runs(project_name=settings.langsmith_project, limit=1)
            logger.info(
                f"LangSmith initialized successfully for project: {settings.langsmith_project}"
            )
            return client
        except Exception as e:
            logger.warning(f"LangSmith connection test failed: {e}")
            return None

    except Exception as e:
        logger.error(f"Failed to initialize LangSmith: {e}")
        return None


def get_common_tags() -> list[str]:
    """Get common tags for tracing."""
    settings = get_settings()
    return [
        "inventra-v1",
        "ai-assistant",
        f"env-{settings.langsmith_environment}",
        "multi-agent",
    ]


def enhanced_traceable(
    name: str, tags: Optional[list[str]] = None, metadata: Optional[dict] = None
):
    """Enhanced traceable decorator with common tags and metadata.

    Args:
        name: Name of the trace
        tags: Additional tags to add to common tags
        metadata: Additional metadata for the trace
    """
    common_tags = get_common_tags()
    all_tags = common_tags + (tags or [])

    return traceable(name=name, tags=all_tags, metadata=metadata or {})


def trace_error(error: Exception, context: dict = None):
    """Trace an error with context information.

    Args:
        error: The exception that occurred
        context: Additional context about the error
    """
    try:
        with trace(
            name="error_occurred",
            inputs={"error_type": type(error).__name__, "context": context or {}},
            tags=get_common_tags() + ["error"],
        ) as run_tree:
            run_tree.error = str(error)
            run_tree.end(error=error)
            logger.error(f"Traced error: {error}", extra={"context": context})
    except Exception as trace_error:
        logger.error(f"Failed to trace error: {trace_error}")


def trace_user_feedback(
    run_id: str, score: float, feedback_text: str = None, correction: str = None
):
    """Submit user feedback to LangSmith.

    Args:
        run_id: The LangSmith run ID to attach feedback to
        score: Feedback score (0.0 to 1.0)
        feedback_text: Optional feedback text
        correction: Optional correction text
    """
    try:
        client = Client()
        client.create_feedback(
            run_id=run_id,
            key="user_satisfaction",
            score=score,
            comment=feedback_text,
            correction=correction,
        )
        logger.info(f"User feedback submitted for run: {run_id}")
    except Exception as e:
        logger.error(f"Failed to submit user feedback: {e}")
