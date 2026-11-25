# 组员 B：Mock Generator 使用与交付说明

## 1. 实现依据与范围

基于 `dev` 分支 `744fba0` 的共享模型和数据契约实现。
以当前 `data-contracts.md`、`contracts/` 和组长最新回复为准：

- 使用 Python 3.11.x 和 Pydantic v2。
- 接口为 `generate(task: Task) -> GenerationResult`，模块间传递模型对象。
- 第一阶段支持 `vector_add`、`float32`，返回固定 Python 示例代码。
- 通过测试替换内部依赖触发失败，不在 Task 或 API 中加入 `mock_should_fail`。
- 本模块不执行生成代码，不调用模型 API，不操作数据库或修改任务状态。

旧的 11 月 19 日会议记录中“字典”和测试字段的安排已被新契约替代。
生成代码演示两个等长一维序列逐元素相加；它是展示用模板，不代表 GPU 实现。
当前 shape 仅按共享契约校验为非空正整数列表，不据此承诺多维代码执行支持。

## 2. 文件与依赖

| 文件 | 用途 |
|---|---|
| `agent/generator.py` | 生成器实现和可替换的内部生成依赖 |
| `agent/__init__.py` | 导出 `generate` |
| `tests/test_generator.py` | 成功、失败、异常输入和模型对接测试 |
| `examples/generator_demo.py` | 打印成功结果的可运行示例 |
| `requirements.txt` | 运行依赖 Pydantic v2 |
| `requirements-dev.txt` | 运行依赖与 pytest |

共享模型的入口原名为 `contracts/init.py`，本次改名为 `contracts/__init__.py`，
内容不变，以使文档约定的 `from contracts import Task` 可用。
没有新增或修改共享模型字段、校验规则及状态枚举。

## 3. 安装与运行

在项目根目录，使用已安装的 Python 3.11：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m examples.generator_demo
```

本机使用 Conda 创建了独立环境，可直接执行：

```powershell
.\.venv\python.exe -m pytest -q
.\.venv\python.exe -m examples.generator_demo
```

虚拟环境和缓存不应提交。拿到源码的其他成员需自行创建环境。

## 4. 后端调用

```python
from agent import generate
from contracts import Task

task = Task(task_id="task_001", operator="vector_add", shape=[4])
result = generate(task)
print(result.model_dump_json(indent=2))
```

后端负责在调用前校验 API 请求、设置 `generating`，并根据返回值流转状态：

```python
from contracts import FailureStage, TaskStatus

if result.success:
    task.status = TaskStatus.GENERATED
    # 将 task、result 和 TestCase 传给执行器。
else:
    task.status = TaskStatus.FAILED
    task.failure_stage = FailureStage.GENERATION_FAILED
    # 保存 result.error，停止后续执行与评估。
```

以上状态代码仅为组长集成时的示例，不在生成模块中执行。
成功和失败都返回同一 `GenerationResult` 类型；通过 HTTP 或 JSON 传递时再序列化。

## 5. 错误处理与失败测试

| 场景 | 返回错误码 |
|---|---|
| 非 Task 输入、任务不符合模型、未支持的算子或 dtype | `INVALID_TASK` |
| 内部生成依赖抛出异常 | `GENERATION_ERROR` |
| 内部生成依赖返回空白或非字符串代码 | `GENERATION_ERROR` |

失败时 `success=False`、`code=None`，`error` 为 `ErrorInfo`。
非法 API 输入主要由后端处理；生成器的检查用于保护独立调用入口。
内部异常文本不直接放进返回值，避免未来接入模型时暴露供应商敏感信息。

测试通过 pytest 的 monkeypatch 替换 `agent.generator._generate_code`：

```python
from agent import generator

def failing_provider(task):
    raise RuntimeError("simulated provider failure")

def test_failure(monkeypatch):
    from contracts import Task

    monkeypatch.setattr(generator, "_generate_code", failing_provider)
    task = Task(task_id="failure_demo", operator="vector_add", shape=[4])
    result = generator.generate(task)
    assert result.success is False
    assert result.error.code == "GENERATION_ERROR"
```

只运行相关测试：

```powershell
.\.venv\python.exe -m pytest tests/test_generator.py -q
.\.venv\python.exe -m pytest tests/test_generator.py -k failure -v
```

测试包含 JSON 往返校验、TaskResult 组装、输入任务不变和失败恢复。
代码检查仅解析固定模板语法，不执行生成源码。
共享模型自身的规则继续由共享层维护，本模块未调整其类型转换行为。

## 6. 提交与验收

当前功能分支为 `feature/generator`，PR 目标为 `dev`。
提交时包含本模块、测试、示例、依赖文件、README 和本说明，以及共享入口改名。
PR 中单独说明共享入口改名的原因和“模型字段未变”。

验收内容：成功生成、模拟失败、异常输入、结果符合共享模型、可重复运行。
最终端到端测试需要组长的后端与 C/D/A 模块到位后共同进行。

### 本次本地验证记录

- 日期：2026-11-25。
- 环境：Windows、Python 3.11.18、Pydantic 2.14.4、pytest 9.2.0。
- 命令：`.\.venv\python.exe -m pytest -q`。
- 结果：`24 passed in 0.58s`。
- 示例：`.\.venv\python.exe -m examples.generator_demo` 正常输出成功 JSON。
- 范围：生成模块单元测试与共享模型对接；尚未进行完整平台端到端联调。

### 建议提交命令

在仓库根目录确认 `git status`，再执行：

```powershell
git add agent tests examples contracts/init.py contracts/__init__.py requirements.txt requirements-dev.txt README.md docs/generator.md
git commit -m "Implement mock generator with shared contracts and tests"
git push -u origin feature/generator
```

随后在 GitHub 创建目标为 `dev` 的 PR，由组长审查。

建议 PR 描述：

> 实现组员 B 的第一阶段 Mock Generator，按共享 Task / GenerationResult 模型返回 vector_add 预设代码。
> 失败通过测试替换内部依赖触发，不新增任务测试字段；任务状态由后端维护。
> 将 contracts/init.py 改名为 __init__.py，修复文档规定的包导入方式，模型内容未变。
> Python 3.11 下 24 项测试通过，示例调用通过；完整平台联调待其他模块接入后完成。
