
"""
Common models and enumerations shared by all modules.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContractModel(BaseModel):
    """
    Base class for all shared data models.

    extra="forbid":
        Do not allow undeclared fields.

    validate_assignment=True:
        Validate values when model attributes are modified.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class TaskStatus(str, Enum):
    """Current status of a task."""

    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    RUNNING = "running"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureStage(str, Enum):
    """Stage where a task failed."""

    GENERATION_FAILED = "generation_failed"
    EXECUTION_FAILED = "execution_failed"
    EVALUATION_FAILED = "evaluation_failed"


class ErrorInfo(ContractModel):
    """Unified error information."""

    code: str = Field(
        min_length=1,
        description="Error code",
    )

    message: str = Field(
        min_length=1,
        description="Human-readable error message",
    )
