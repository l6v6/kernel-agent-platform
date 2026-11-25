"""Contract, success, failure and defensive-input tests for member B."""

import ast
import json

import pytest
from pydantic import ValidationError

from agent import generate
from agent import generator
from contracts import ErrorInfo, GenerationResult, Task, TaskStatus


@pytest.fixture
def task():
    return Task(task_id="task_001", operator="vector_add", shape=[4])


def assert_failure(result, code):
    assert isinstance(result, GenerationResult)
    assert result.success is False
    assert result.code is None
    assert result.language == "python"
    assert isinstance(result.error, ErrorInfo)
    assert result.error.code == code
    assert result.error.message
    assert GenerationResult.model_validate_json(result.model_dump_json()) == result


def test_success_returns_shared_model_and_serializable_code(task):
    result = generate(task)
    assert isinstance(result, GenerationResult)
    assert result.success is True
    assert result.language == "python"
    assert result.error is None
    assert result.code.strip()
    # Parse only: no generated source is executed in phase one.
    source = ast.parse(result.code)
    function = source.body[0]
    assert isinstance(function, ast.FunctionDef)
    assert function.name == "vector_add"
    assert [arg.arg for arg in function.args.args] == ["a", "b"]
    assert set(json.loads(result.model_dump_json())) == {
        "success", "code", "language", "error"
    }
    assert GenerationResult.model_validate_json(result.model_dump_json()) == result


def test_preset_generation_is_repeatable(task):
    assert generate(task) == generate(task)


def test_generation_does_not_update_task_state(task):
    before = task.model_dump()
    generate(task)
    assert task.model_dump() == before
    assert task.status == TaskStatus.PENDING


def test_mock_provider_failure_and_recovery(task, monkeypatch):
    before = task.model_dump()

    def fail(_task):
        raise RuntimeError("private provider details")

    with monkeypatch.context() as patch:
        patch.setattr(generator, "_generate_code", fail)
        result = generate(task)
    assert_failure(result, "GENERATION_ERROR")
    assert "private provider details" not in result.error.message
    assert task.model_dump() == before
    assert generate(task).success is True


@pytest.mark.parametrize("code", [None, "", " \n\t", 123, [], {}])
def test_invalid_provider_output(task, monkeypatch, code):
    monkeypatch.setattr(generator, "_generate_code", lambda _task: code)
    assert_failure(generate(task), "GENERATION_ERROR")


@pytest.mark.parametrize("value", [None, {}, [], "vector_add", 123])
def test_direct_call_requires_task_model(value):
    assert_failure(generate(value), "INVALID_TASK")


@pytest.mark.parametrize("change", [
    {"operator": "relu"},
    {"dtype": "float64"},
    {"shape": []},
    {"shape": [0]},
    {"shape": [-1]},
    {"task_id": ""},
])
def test_invalid_task_does_not_call_provider(task, monkeypatch, change):
    def should_not_run(_task):
        pytest.fail("Invalid tasks must not reach the generator dependency")

    monkeypatch.setattr(generator, "_generate_code", should_not_run)
    assert_failure(generate(task.model_copy(update=change)), "INVALID_TASK")


def test_provider_receives_independent_task_copy(task, monkeypatch):
    before = task.model_dump()

    def provider(copy):
        copy.shape.append(8)
        copy.description = "changed by provider"
        return "def vector_add(a, b):\n    return []\n"

    monkeypatch.setattr(generator, "_generate_code", provider)
    assert generate(task).success is True
    assert task.model_dump() == before


def test_backend_can_assemble_result_using_shared_contract(task):
    from contracts import TaskResult

    result = TaskResult(task=task, generation=generate(task))
    assert result.generation.success is True
    assert result.execution is None
    assert result.task.status == TaskStatus.PENDING


def test_shared_task_rejects_test_only_flags(task):
    with pytest.raises(ValidationError):
        Task.model_validate({**task.model_dump(), "mock_should_fail": True})
