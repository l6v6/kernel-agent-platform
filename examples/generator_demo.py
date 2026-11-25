"""Run from the repository root: python -m examples.generator_demo."""

from agent import generate
from contracts import Task


def main() -> None:
    task = Task(task_id="demo_001", operator="vector_add", shape=[4])
    result = generate(task)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
