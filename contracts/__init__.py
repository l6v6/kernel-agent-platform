
"""
Shared data models for the kernel-agent-platform project.

Other modules should import models from this package.
"""

from .common import (
    ContractModel,
    ErrorInfo,
    TaskStatus,
    FailureStage,
)

from .task import (
    TaskCreate,
    Task,
    TestCase,
)

from .results import (
    GenerationResult,
    ExecutionResult,
    EvaluationResult,
    BenchmarkResult,
    TaskResult,
)

__all__ = [
    "ContractModel",
    "ErrorInfo",
    "TaskStatus",
    "FailureStage",
    "TaskCreate",
    "Task",
    "TestCase",
    "GenerationResult",
    "ExecutionResult",
    "EvaluationResult",
    "BenchmarkResult",
    "TaskResult",
]
