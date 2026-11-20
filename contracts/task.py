
"""
Task-related shared data models.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import Field, field_validator

from .common import ContractModel, TaskStatus, FailureStage


class TaskCreate(ContractModel):
    """
    Data submitted by the frontend when creating a task.
    """

    operator: str = Field(
        min_length=1,
        description="Operator name",
    )

    description: str | None = Field(
        default=None,
        description="Task description",
    )

    shape: list[int] = Field(
        min_length=1,
        description="Tensor shape",
    )

    dtype: str = Field(
        default="float32",
        min_length=1,
        description="Data type",
    )

    @field_validator("shape")
    @classmethod
    def validate_shape(cls, value: list[int]) -> list[int]:
        """
        Every dimension in shape must be a positive integer.
        """

        if any(
            isinstance(dim, bool)
            or not isinstance(dim, int)
            or dim <= 0
            for dim in value
        ):
            raise ValueError(
                "Every dimension in shape must be a positive integer"
            )

        return value


class Task(TaskCreate):
    """
    Complete task information managed by the backend.
    """

    task_id: str = Field(
        min_length=1,
        description="Unique task ID",
    )

    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status",
    )

    failure_stage: FailureStage | None = Field(
        default=None,
        description="Stage where the task failed",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task creation time",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update time",
    )


class TestCase(ContractModel):
    """
    Test case used by the executor and evaluator.
    """

    case_id: str = Field(
        min_length=1,
        description="Unique test case ID",
    )

    inputs: dict[str, Any] = Field(
        description="Input data for the operator",
    )

    expected_output: Any = Field(
        description="Expected output",
    )

    tolerance: float = Field(
        default=0.0001,
        ge=0,
        description="Allowed floating-point error",
    )
