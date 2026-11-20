
"""
Result models returned by different modules.
"""

from typing import Any

from pydantic import Field, model_validator

from .common import ContractModel, ErrorInfo
from .task import Task


class GenerationResult(ContractModel):
    """
    Result returned by the agent module.
    """

    success: bool = Field(
        description="Whether code generation succeeded",
    )

    code: str | None = Field(
        default=None,
        description="Generated source code",
    )

    language: str = Field(
        default="python",
        description="Programming language",
    )

    error: ErrorInfo | None = Field(
        default=None,
        description="Error information",
    )

    @model_validator(mode="after")
    def validate_result(self):
        """
        Successful generation must contain code.
        Failed generation must contain error information.
        """

        if self.success:
            if not self.code:
                raise ValueError(
                    "Successful generation must contain code"
                )

            if self.error is not None:
                raise ValueError(
                    "Successful generation cannot contain an error"
                )

        else:
            if self.error is None:
                raise ValueError(
                    "Failed generation must contain error information"
                )

            if self.code is not None:
                raise ValueError(
                    "Failed generation cannot contain code"
                )

        return self


class ExecutionResult(ContractModel):
    """
    Result returned by the executor module.
    """

    success: bool = Field(
        description="Whether execution succeeded",
    )

    output: Any = Field(
        default=None,
        description="Actual execution output",
    )

    error: ErrorInfo | None = Field(
        default=None,
        description="Error information",
    )

    @model_validator(mode="after")
    def validate_result(self):
        """
        Successful execution cannot contain an error.
        Failed execution must contain error information.
        """

        if self.success and self.error is not None:
            raise ValueError(
                "Successful execution cannot contain an error"
            )

        if not self.success and self.error is None:
            raise ValueError(
                "Failed execution must contain error information"
            )

        if not self.success and self.output is not None:
            raise ValueError(
                "Failed execution cannot contain output"
            )

        return self


class EvaluationResult(ContractModel):
    """
    Result returned by the correctness evaluator.
    """

    passed: bool = Field(
        description="Whether correctness evaluation passed",
    )

    expected: Any = Field(
        description="Expected output",
    )

    actual: Any = Field(
        description="Actual output",
    )

    max_abs_error: float | None = Field(
        default=None,
        ge=0,
        description="Maximum absolute error",
    )

    tolerance: float = Field(
        default=0.0001,
        ge=0,
        description="Allowed error tolerance",
    )

    message: str = Field(
        description="Evaluation message",
    )


class BenchmarkResult(ContractModel):
    """
    Performance measurement result.
    """

    latency_ms: float = Field(
        ge=0,
        description="Latency in milliseconds",
    )

    is_simulated: bool = Field(
        default=True,
        description="Whether this is simulated performance data",
    )

    measurement_method: str = Field(
        default="mock",
        description="Measurement method",
    )

    note: str | None = Field(
        default=None,
        description="Additional information",
    )


class TaskResult(ContractModel):
    """
    Combined result of the entire task pipeline.

    Some fields can be None if the task has not reached
    the corresponding stage or failed before that stage.
    """

    task: Task = Field(
        description="Basic task information",
    )

    generation: GenerationResult | None = Field(
        default=None,
        description="Code generation result",
    )

    execution: ExecutionResult | None = Field(
        default=None,
        description="Execution result",
    )

    evaluation: EvaluationResult | None = Field(
        default=None,
        description="Correctness evaluation result",
    )

    benchmark: BenchmarkResult | None = Field(
        default=None,
        description="Performance measurement result",
    )
