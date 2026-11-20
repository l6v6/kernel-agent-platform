# 模块数据契约说明

1. 数据契约与共享模型

1.1 什么是数据契约

数据契约（Data Contract）用于规定不同模块之间传递的数据结构和接口规范，主要包括：

数据包含哪些字段；

每个字段的数据类型；

哪些字段是必填项；

字段的具体含义；

模块之间如何传递数据；

数据不符合要求时如何处理。

本项目包含 backend、agent、executor、evaluator、storage 和 frontend 等多个模块。不同模块需要交换任务信息、代码生成结果、执行结果和评估结果。

如果每个模块自行定义数据格式，容易出现字段名称不一致、数据类型不一致以及接口无法直接对接等问题。

因此，项目在开发初期统一制定数据契约，并通过共享数据模型保证模块之间的数据格式一致。

1.2 为什么使用 Pydantic

本项目第一阶段使用 Pydantic v2 定义共享数据模型。

Pydantic 是一个 Python 数据校验和数据序列化库，可以根据开发者定义的模型检查数据是否符合预期。

例如：

from pydantic import BaseModel

class Example(BaseModel):
    name: str
    age: int

使用这个模型创建数据时，Pydantic 会根据字段定义进行校验：

example = Example(
    name="test",
    age=18
)

如果传入的数据不符合模型要求，就会产生数据校验错误。

本项目使用 Pydantic 的主要原因：

统一数据格式：不同模块使用相同的模型，避免重复定义。

自动数据校验：检查必填字段、数据类型和约束条件，减少错误数据进入模块。

提高代码可读性：通过模型定义可以直接了解函数需要接收什么数据、返回什么结果。

方便模块集成：上游模块返回的模型可以直接传递给下游模块。

方便 API 数据处理：Pydantic 支持将模型转换为字典和 JSON，便于 FastAPI 接收和返回数据。

需要注意，Pydantic 负责数据结构定义、校验和序列化，不负责任务调度、算子生成、算子执行或数据库存储。这些功能仍然由各自的业务模块完成。

1.3 共享模型的存放位置

所有模块共同使用的数据模型统一放在项目根目录的 contracts/ 文件夹中。

目录结构：

kernel-agent-platform/
├── contracts/
│   ├── __init__.py
│   ├── common.py
│   ├── task.py
│   └── results.py
├── backend/
├── agent/
├── executor/
├── evaluator/
├── storage/
├── frontend/
└── tests/

各文件的职责：

文件

职责

__init__.py

统一导出共享模型，方便其他模块导入

common.py

定义基础模型、错误信息、任务状态和失败阶段

task.py

定义任务创建请求、正式任务和测试用例

results.py

定义生成结果、执行结果、正确性评估结果、性能评估结果和统一任务结果

选择将 contracts/ 放在项目根目录，是因为它属于整个系统的公共数据层，不应依赖某一个具体业务模块。

1.4 Pydantic 模型的基本使用方式

本项目的共享模型继承统一的 ContractModel，而 ContractModel 继承 Pydantic 的 BaseModel。

from pydantic import BaseModel, ConfigDict

class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )

其中：

BaseModel：Pydantic 提供的基础模型类。

ConfigDict：用于设置模型的校验和配置规则。

extra="forbid"：不允许出现模型中没有定义的额外字段。

validate_assignment=True：修改模型属性时也执行数据校验。

其他共享模型继承 ContractModel，从而使用统一的校验规则。

例如：

class ErrorInfo(ContractModel):
    code: str
    message: str

1.5 本项目使用的 Pydantic 功能

功能

作用

项目中的用途

BaseModel

定义数据模型

定义 Task、TestCase 等

Field

设置字段约束和默认值

设置必填项、默认值和数值范围

field_validator

对单个字段进行自定义校验

检查 shape 是否全部为正整数

model_validator

对整个模型进行联合校验

检查生成成功时是否存在 code

ConfigDict

设置模型行为

禁止额外字段、开启赋值校验

Enum

定义固定选项

统一任务状态和失败阶段

model_dump()

将模型转换为 Python 字典

用于数据处理和持久化前转换

model_dump_json()

将模型转换为 JSON 字符串

用于 JSON 序列化

本项目使用 Python 3.11 和 Pydantic v2，因此使用 field_validator、model_validator 等 v2 风格的接口，不使用 Pydantic v1 的 validator 和 root_validator 写法。

1.6 共享模型与业务模块的关系

共享模型只负责定义数据格式，不负责实现业务逻辑。

各模块通过导入共享模型使用统一的数据结构。

例如：

from contracts import Task, GenerationResult

def generate(task: Task) -> GenerationResult:
    ...

这里：

Task 规定生成模块接收什么数据；

GenerationResult 规定生成模块返回什么数据；

generate() 才是真正执行代码生成业务逻辑的函数。

这样可以将数据结构和业务逻辑分开，降低模块之间的耦合程度。

1.7 数据模型的修改原则

共享模型是各模块共同遵守的接口约定，不能由某个组员随意修改。

如果开发过程中确实需要增加或修改字段，应遵循以下步骤：

提出修改原因和使用场景。

检查修改是否影响其他模块。

与项目负责人及相关模块开发人员讨论。

统一修改 contracts/ 中的模型。

同步修改 data-contracts.md 和 api.md。

修改相关模块和单元测试。

通过集成测试后再合并。

所有模块应优先保持共享模型稳定，避免因频繁修改数据结构而增加集成成本。

## 2. 通用数据约定

### 2.1 数据模型

本项目使用 Pydantic 的 `BaseModel` 定义数据模型。

例如：

```python
from pydantic import BaseModel

class Example(BaseModel):
    name: str
    age: int
```

创建模型时，Pydantic 会检查字段类型和数据是否合法。

模块之间传递时使用模型对象；通过 HTTP API 或保存为 JSON 时，使用模型的 JSON 序列化结果。

### 2.2 通用错误信息 ErrorInfo

错误信息统一采用以下结构：

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `code` | `str` | 是 | 错误代码 |
| `message` | `str` | 是 | 错误描述 |

示例：

```json
{
  "code": "GENERATION_ERROR",
  "message": "Mock generation failed"
}
```

建议错误代码：

| 错误代码 | 含义 |
|---|---|
| `INVALID_TASK` | 任务数据不合法 |
| `GENERATION_ERROR` | 算子代码生成失败 |
| `EXECUTION_ERROR` | 执行过程失败 |
| `EVALUATION_ERROR` | 正确性评估失败 |
| `TASK_NOT_FOUND` | 找不到指定任务 |
| `INTERNAL_ERROR` | 未预期的内部错误 |

### 2.3 任务状态 TaskStatus

任务状态统一使用以下枚举值：

| 状态 | 含义 |
|---|---|
| `pending` | 任务已创建，等待处理 |
| `generating` | 正在生成算子代码 |
| `generated` | 算子代码已生成 |
| `running` | 正在执行算子 |
| `evaluating` | 正在进行正确性评估 |
| `completed` | 任务全部完成 |
| `failed` | 任务失败 |

失败阶段通过 `failure_stage` 单独表示：

| 失败阶段 | 含义 |
|---|---|
| `generation_failed` | 代码生成阶段失败 |
| `execution_failed` | 算子执行阶段失败 |
| `evaluation_failed` | 正确性评估阶段失败 |

注意：失败阶段不是新的任务状态。任务失败时，`status` 统一为 `failed`。

## 3. Task：任务数据

### 3.1 TaskCreate：创建任务请求

前端向 backend 提交任务时，使用 `TaskCreate`。

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `operator` | `str` | 是 | 算子名称 |
| `description` | `str \| None` | 否 | 任务描述 |
| `shape` | `list[int]` | 是 | 张量形状 |
| `dtype` | `str` | 否 | 数据类型，默认 `float32` |

第一阶段只支持 `vector_add` 算子和 `float32` 数据类型。

请求示例：

```json
{
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32"
}
```

### 3.2 Task：正式任务

backend 接收到创建请求后，生成唯一的 `task_id`，并创建正式任务。

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `task_id` | `str` | 是 | 唯一任务编号 |
| `operator` | `str` | 是 | 算子名称 |
| `description` | `str \| None` | 否 | 任务描述 |
| `shape` | `list[int]` | 是 | 张量形状 |
| `dtype` | `str` | 是 | 数据类型 |
| `status` | `TaskStatus` | 是 | 当前任务状态 |
| `failure_stage` | `FailureStage \| None` | 否 | 失败阶段 |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 最近更新时间 |

正式任务示例：

```json
{
  "task_id": "task_001",
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32",
  "status": "pending",
  "failure_stage": null,
  "created_at": "2026-11-20T10:00:00Z",
  "updated_at": "2026-11-20T10:00:00Z"
}
```

注意：

1. `task_id` 由 backend 创建，不由前端指定。
2. `status` 由 backend 和任务流程管理。
3. `failure_stage` 仅在任务失败时填写。
4. `shape` 中的每个维度必须是正整数。

## 4. TestCase：测试用例

测试用例用于描述执行算子时的输入数据、预期输出和误差容忍范围。

backend 或任务编排流程负责为任务准备测试用例，并将其交给 executor 和 evaluator。

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `case_id` | `str` | 是 | 测试用例编号 |
| `inputs` | `dict[str, Any]` | 是 | 算子输入数据 |
| `expected_output` | `Any` | 是 | 预期输出 |
| `tolerance` | `float` | 否 | 浮点数误差容忍范围，默认 `0.0001` |

示例：

```json
{
  "case_id": "case_001",
  "inputs": {
    "a": [1, 2, 3, 4],
    "b": [5, 6, 7, 8]
  },
  "expected_output": [6, 8, 10, 12],
  "tolerance": 0.0001
}
```

第一阶段的 `vector_add` 测试用例使用两个向量作为输入。

后续支持其他算子时，可以根据算子类型扩展输入结构，不需要改变整个任务数据模型。

## 5. GenerationResult：代码生成结果

所属模块：`agent/`

函数接口：

```python
generate(task: Task) -> GenerationResult
```

生成模块接收任务数据，返回生成结果。

### 5.1 成功示例

```json
{
  "success": true,
  "code": "def vector_add(a, b): return a + b",
  "language": "python",
  "error": null
}
```

### 5.2 失败示例

```json
{
  "success": false,
  "code": null,
  "language": "python",
  "error": {
    "code": "GENERATION_ERROR",
    "message": "Mock generation failed"
  }
}
```

字段说明：

| 字段 | 类型 | 含义 |
|---|---|---|
| `success` | `bool` | 是否生成成功 |
| `code` | `str \| None` | 生成的代码 |
| `language` | `str` | 代码语言 |
| `error` | `ErrorInfo \| None` | 错误信息 |

约定：

1. 生成成功时，`code` 必须存在，`error` 为 `None`。
2. 生成失败时，`code` 为 `None`，`error` 必须存在。
3. 第一阶段使用 Mock Generator 返回预先定义的代码。
4. 后续接入真实模型时，尽量保持该接口不变。

## 6. ExecutionResult：执行结果

所属模块：`executor/`

函数接口：

```python
run(
    task: Task,
    generation_result: GenerationResult,
    test_case: TestCase
) -> ExecutionResult
```

执行模块接收任务、生成结果和测试用例，返回执行结果。

### 6.1 成功示例

```json
{
  "success": true,
  "output": [6, 8, 10, 12],
  "error": null
}
```

### 6.2 失败示例

```json
{
  "success": false,
  "output": null,
  "error": {
    "code": "EXECUTION_ERROR",
    "message": "Mock execution failed"
  }
}
```

字段说明：

| 字段 | 类型 | 含义 |
|---|---|---|
| `success` | `bool` | 是否执行成功 |
| `output` | `Any` | 实际输出结果 |
| `error` | `ErrorInfo \| None` | 错误信息 |

约定：

1. 执行成功时，`output` 保存实际输出，`error` 为 `None`。
2. 执行失败时，`output` 为 `None`，`error` 必须存在。
3. 第一阶段使用受控 Mock Executor 返回模拟执行结果。
4. 第一阶段不执行任意生成代码。
5. 后续接入真实 GPU 执行环境时，尽量保持该接口不变。

## 7. EvaluationResult：正确性评估结果

所属模块：`evaluator/`

函数接口：

```python
evaluate(
    expected,
    actual,
    tolerance
) -> EvaluationResult
```

评估模块比较预期输出和实际输出，判断算子计算结果是否正确。

示例：

```json
{
  "passed": true,
  "expected": [6, 8, 10, 12],
  "actual": [6, 8, 10, 12],
  "max_abs_error": 0.0,
  "tolerance": 0.0001,
  "message": "结果一致"
}
```

字段说明：

| 字段 | 类型 | 含义 |
|---|---|---|
| `passed` | `bool` | 是否通过正确性检查 |
| `expected` | `Any` | 预期输出 |
| `actual` | `Any` | 实际输出 |
| `max_abs_error` | `float \| None` | 最大绝对误差 |
| `tolerance` | `float` | 误差容忍范围 |
| `message` | `str` | 评估说明 |

第一阶段评估规则：

1. 首先检查预期输出和实际输出的长度或形状是否一致。
2. 然后比较对应元素的绝对误差。
3. 所有元素的绝对误差均不超过 `tolerance` 时，判定为通过。
4. 如果执行失败，则不进入正常的正确性比较流程。

## 8. BenchmarkResult：性能评估结果

所属模块：`evaluator/`

函数接口：

```python
measure(...) -> BenchmarkResult
```

第一阶段仅记录模拟性能数据。

示例：

```json
{
  "latency_ms": 0.01,
  "is_simulated": true,
  "measurement_method": "mock",
  "note": "模拟记录，不代表真实 GPU 性能"
}
```

字段说明：

| 字段 | 类型 | 含义 |
|---|---|---|
| `latency_ms` | `float` | 延迟，单位为毫秒 |
| `is_simulated` | `bool` | 是否为模拟数据 |
| `measurement_method` | `str` | 测量方式 |
| `note` | `str \| None` | 补充说明 |

约定：

1. 第一阶段 `is_simulated` 必须为 `true`。
2. `measurement_method` 使用 `mock`。
3. 模拟延迟不能作为真实 GPU 性能数据。
4. 后续真实 GPU 阶段再增加设备型号、预热次数、测量次数和统计指标。

## 9. TaskResult：统一任务结果

`TaskResult` 用于汇总一个任务的完整执行结果。

字段说明：

| 字段 | 类型 | 含义 |
|---|---|---|
| `task` | `Task` | 任务基本信息 |
| `generation` | `GenerationResult \| None` | 代码生成结果 |
| `execution` | `ExecutionResult \| None` | 执行结果 |
| `evaluation` | `EvaluationResult \| None` | 正确性评估结果 |
| `benchmark` | `BenchmarkResult \| None` | 性能评估结果 |

示例：

```json
{
  "task": {
    "task_id": "task_001",
    "operator": "vector_add",
    "description": "计算两个向量对应位置元素之和",
    "shape": [4],
    "dtype": "float32",
    "status": "completed",
    "failure_stage": null,
    "created_at": "2026-11-20T10:00:00Z",
    "updated_at": "2026-11-20T10:00:01Z"
  },
  "generation": {
    "success": true,
    "code": "def vector_add(a, b): return a + b",
    "language": "python",
    "error": null
  },
  "execution": {
    "success": true,
    "output": [6, 8, 10, 12],
    "error": null
  },
  "evaluation": {
    "passed": true,
    "expected": [6, 8, 10, 12],
    "actual": [6, 8, 10, 12],
    "max_abs_error": 0.0,
    "tolerance": 0.0001,
    "message": "结果一致"
  },
  "benchmark": {
    "latency_ms": 0.01,
    "is_simulated": true,
    "measurement_method": "mock",
    "note": "模拟记录，不代表真实 GPU 性能"
  }
}
```

注意：

- 如果任务在生成阶段失败，后续的 `execution`、`evaluation` 和 `benchmark` 可以为 `None`。
- 如果任务在执行阶段失败，`generation` 可以保留，`execution` 保存失败信息，后续结果可以为 `None`。
- 如果任务在正确性评估阶段失败，应保留已经产生的生成和执行结果。
- 任务失败时，应通过 `Task.status` 和 `Task.failure_stage` 表示失败状态。

## 10. Mock 测试约定

Mock 用于第一阶段在没有真实模型 API 和真实 GPU 环境时，稳定地测试各模块。

约定：

1. 正式的 `Task` 模型中不包含 `mock_should_fail`。
2. Mock 成功和失败由测试代码控制。
3. 可以使用 pytest 的 `monkeypatch`、Mock 或 Stub 替换模块内部依赖。
4. 不要为了测试方便，在正式 API 请求和任务数据中加入仅供测试使用的字段。
5. 测试应覆盖成功、失败和异常输入等情况。

## 11. 模块接口汇总

| 模块 | 函数 | 输入 | 输出 |
|---|---|---|---|
| agent | `generate(task)` | `Task` | `GenerationResult` |
| executor | `run(task, generation_result, test_case)` | `Task`、`GenerationResult`、`TestCase` | `ExecutionResult` |
| evaluator | `evaluate(expected, actual, tolerance)` | 预期输出、实际输出、容差 | `EvaluationResult` |
| evaluator | `measure(...)` | 性能测量相关数据 | `BenchmarkResult` |
| backend | 任务编排流程 | 任务及各模块结果 | `TaskResult` |
| storage | 保存和读取任务 | `Task`、`TaskResult` | 持久化记录 |

## 12. 数据契约与代码的关系

项目开发时遵循以下顺序：

首先确定数据字段和模块接口。

在 contracts/ 中使用 Pydantic 定义对应模型。

各业务模块从 contracts/ 导入模型。

各模块按照数据契约实现函数。

每个模块编写独立的单元测试。

集成时检查上游输出能否直接传递给下游模块。

如需修改共享模型，应同步更新文档、代码和测试。

数据契约文档是模块接口设计的依据，contracts/ 中的 Python 代码则是这些约定的实际实现。
