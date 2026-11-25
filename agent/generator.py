"""Phase-one mock generator using the project's shared contracts.

The returned source is a fixed demonstration template. This module neither
executes that source nor updates task state, storage, or performance records.
"""

from pydantic import ValidationError

from contracts import ErrorInfo, GenerationResult, Task


def _generate_code(task: Task) -> str:
    """Return preset Python source; tests may replace this dependency."""
    return (
        "def vector_add(a, b):\n"
        '    """Add two equal-length vectors element by element."""\n'
        "    return [x + y for x, y in zip(a, b, strict=True)]\n"
    )


def _failure(code: str, message: str) -> GenerationResult:
    return GenerationResult(
        success=False,
        code=None,
        language="python",
        error=ErrorInfo(code=code, message=message),
    )


def generate(task: Task) -> GenerationResult:
    """Generate mock vector_add source for a validated Task.

    API validation belongs to backend. Defensive checks here also handle
    incorrect direct calls and models constructed without normal validation.
    Generation failures are returned as shared models, not task-state changes.
    """
    if not isinstance(task, Task):
        return _failure("INVALID_TASK", "Expected a contracts.Task instance.")

    try:
        # Validate a copy even if the caller used model_construct/model_copy.
        # The provider receives this copy so it cannot mutate the caller's task.
        checked_task = Task.model_validate(task.model_dump())
    except ValidationError:
        return _failure("INVALID_TASK", "Task does not satisfy the shared contract.")

    if checked_task.operator != "vector_add":
        return _failure("INVALID_TASK", "Only vector_add is supported in phase one.")
    if checked_task.dtype != "float32":
        return _failure("INVALID_TASK", "Only float32 is supported in phase one.")

    try:
        code = _generate_code(checked_task)
        if not isinstance(code, str) or not code.strip():
            return _failure("GENERATION_ERROR", "Generator returned empty or invalid code.")
        return GenerationResult(success=True, code=code, language="python", error=None)
    except Exception:
        # Keep provider details (possibly credentials in a future API client)
        # out of the result exposed to the frontend.
        return _failure("GENERATION_ERROR", "Mock code generation failed.")
