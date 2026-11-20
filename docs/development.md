# 开发与协作规范

## 1. 基本原则

- `main` 分支应保持可运行、可演示。
- 每个功能在独立分支开发，通过 Pull Request（PR）合并。
- 每个任务应有清楚的验收标准。
- 不提交密钥、个人令牌、虚拟环境、缓存、数据库临时文件或大体积生成产物。
- 功能只有在实际验证后才能标记为完成。

## 2. 分支命名

建议使用以下格式：

- `feature/task-api`：新功能
- `fix/timeout-handling`：问题修复
- `docs/update-api-docs`：文档修改
- `test/relu-correctness`：测试相关

分支名称简短、清楚，尽量使用英文小写和连字符。

## 3. 推荐开发流程

```text
同步 main
  ↓
创建功能分支
  ↓
编写代码与测试
  ↓
本地运行相关测试
  ↓
git add + git commit
  ↓
git push
  ↓
创建 Pull Request
  ↓
组员 Review
  ↓
合并到 main
```

常用命令：

```bash
git switch main
git pull origin main
git switch -c feature/your-feature
# 修改代码
git status
git add path/to/changed-files
git commit -m "Add task creation API"
git push -u origin feature/your-feature
```

完成 PR 合并后：

```bash
git switch main
git pull origin main
git branch -d feature/your-feature
```

如果分支删除失败或仍有未合并修改，不要强制删除；先确认修改是否已安全保存。

## 4. Commit 规范

提交说明应描述本次修改，例如：

- `Add task creation API`
- `Implement ReLU correctness test`
- `Document experiment protocol`
- `Fix task status update`

避免只写 `update`、`test`、`修改一下` 等无法定位内容的说明。

## 5. Pull Request 检查清单

- [ ] 说明本次改动与原因
- [ ] 关联对应 Issue（如有）
- [ ] 已运行相关测试
- [ ] 没有提交密钥或不必要的大文件
- [ ] 文档和配置已同步更新
- [ ] 至少一名组员完成 Review
- [ ] 说明已知限制和未完成事项

## 6. Python 代码建议

- 使用清晰、可读的变量名。
- 一个函数尽量只承担一个主要职责。
- 对外部输入进行校验。
- 对可能失败的 API、文件和进程操作进行异常处理。
- 日志中避免输出 API Key、令牌或敏感数据。
- 为核心逻辑编写测试。

## 7. 测试约定

- 单元测试：验证独立函数或模块。
- 集成测试：验证多个模块之间的接口。
- 端到端测试：验证用户提交任务到查看结果的完整链路。

涉及 GPU 的测试应记录硬件、驱动、软件版本和输入配置。若测试因环境缺失无法运行，要明确标注，不能声称通过。

## 8. 每周迭代约定

每个迭代开始前确认目标、负责人、协作者、依赖和验收标准。结束时演示成果、检查测试、记录遗留问题，并轮换主责，让每位成员持续接触不同模块。

## 9. 安全注意事项

- `.env` 等本地密钥文件不得提交。
- `.env.example` 只能放变量名和虚构占位值。
- 不要在 Web 后端主进程直接执行不可信的模型生成代码。
- 执行代码时应使用隔离环境，并设置超时与资源限制。

## 10. 新成员启动步骤

1. Clone 仓库。
2. 阅读本文件与 `architecture.md`。
3. 按 `README.md` 配置环境。
4. 运行基础测试。
5. 从小型 Issue 开始，创建分支并提交 PR。


## 共享模型的使用规范

### 1. 安装依赖

本项目使用 Python 3.11.x 和 Pydantic v2。

在项目根目录执行：

```bash
pip install "pydantic>=2.7,<3.0"
```

查看安装版本：

```bash
python -c "import pydantic; print(pydantic.__version__)"
```

应显示 `2.x.x`。

如果项目使用 `requirements.txt` 统一管理依赖，应从该文件安装：

```bash
pip install -r requirements.txt
```

### 2. 导入共享模型

所有业务模块统一从项目根目录的 `contracts` 包导入共享模型。

推荐写法：

```python
from contracts import (
    Task,
    TaskCreate,
    TestCase,
    GenerationResult,
    ExecutionResult,
    EvaluationResult,
    BenchmarkResult,
    TaskResult,
    ErrorInfo,
)
```

不要在自己的模块中重新定义这些共享模型。

### 3. 使用模型创建数据

例如，backend 创建一个正式任务：

```python
from contracts import Task, TaskStatus

task = Task(
    task_id="task_001",
    operator="vector_add",
    shape=[4],
    dtype="float32",
    status=TaskStatus.PENDING,
)
```

Pydantic 会检查字段是否符合模型要求。

如果传入不合法的数据，会产生 `ValidationError`。

### 4. 使用模型作为函数参数和返回值

各模块按照数据契约使用统一的函数接口。

agent：

```python
from contracts import Task, GenerationResult

def generate(task: Task) -> GenerationResult:
    ...
```

executor：

```python
from contracts import (
    Task,
    GenerationResult,
    TestCase,
    ExecutionResult,
)

def run(
    task: Task,
    generation_result: GenerationResult,
    test_case: TestCase,
) -> ExecutionResult:
    ...
```

evaluator：

```python
from contracts import EvaluationResult

def evaluate(expected, actual, tolerance) -> EvaluationResult:
    ...
```

各组员应根据这些接口实现模块内部逻辑，不要自行修改函数的输入输出约定。

### 5. 模型转换和序列化

Pydantic 模型可以转换为普通 Python 字典：

```python
task_dict = task.model_dump()
```

也可以转换为 JSON 字符串：

```python
task_json = task.model_dump_json(indent=2)
```

如果需要从字典创建模型：

```python
task = Task.model_validate(task_dict)
```

这些方法可以用于 API 数据处理、数据库读写前的数据转换以及测试。

注意：`model_dump()` 默认会将 Enum 转换为对应的枚举值，便于后续数据处理。

### 6. 异常处理

当输入数据不符合模型约定时，Pydantic 会抛出 `ValidationError`。

例如：

```python
from pydantic import ValidationError
from contracts import TaskCreate

try:
    request = TaskCreate(
        operator="vector_add",
        shape=[-1],
    )
except ValidationError as error:
    print(error)
```

backend 应负责将正式 API 输入校验错误转换为统一的 HTTP 错误响应。

其他业务模块也应根据各自职责处理输入错误，不应让未处理异常直接中断整个任务流程。

### 7. 修改共享模型的规范

共享模型由项目统一维护。

如果某个模块需要增加字段或调整接口：

1. 先说明需要修改的原因。
2. 检查其他模块是否依赖相关字段。
3. 与项目负责人沟通。
4. 修改 `contracts/` 中的模型。
5. 同步修改数据契约文档和 API 文档。
6. 更新相关模块和测试。
7. 提交 PR，由项目负责人检查后合并。

未经讨论，不要直接删除或修改其他模块正在使用的字段。

### 8. 单元测试要求

每个模块至少覆盖：

- 正常输入和成功结果；
- 不合法输入；
- 模拟失败情况；
- 返回结果是否符合共享模型。

Mock 测试通过测试替身或依赖替换实现，不应为了测试方便向正式任务模型添加测试专用字段。
