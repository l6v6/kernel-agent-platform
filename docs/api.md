# API 接口文档

## 1. 基本约定

本项目第一阶段通过 HTTP REST API 实现前端与 backend 之间的通信。

- API 前缀：`/api`
- 数据格式：JSON
- 第一阶段支持的算子：`vector_add`
- 第一阶段支持的数据类型：`float32`

API 请求和响应中的数据结构应与 `contracts/` 中定义的 Pydantic 模型保持一致。

## 2. 统一任务状态

任务状态统一使用以下值：

| 状态 | 含义 |
|---|---|
| `pending` | 任务已创建，等待处理 |
| `generating` | 正在生成算子代码 |
| `generated` | 算子代码已生成 |
| `running` | 正在执行算子 |
| `evaluating` | 正在进行正确性评估 |
| `completed` | 任务全部完成 |
| `failed` | 任务失败 |

失败阶段通过 `failure_stage` 表示：

| 失败阶段 | 含义 |
|---|---|
| `generation_failed` | 代码生成阶段失败 |
| `execution_failed` | 算子执行阶段失败 |
| `evaluation_failed` | 正确性评估阶段失败 |

注意：失败阶段不是新的任务状态。任务失败时，`status` 为 `failed`。

## 3. 通用错误响应

当 API 请求出现错误时，统一返回以下结构：

```json
{
  "detail": {
    "code": "INVALID_REQUEST",
    "message": "shape must contain positive integers"
  }
}
```

常见错误代码：

| 错误代码 | 含义 |
|---|---|
| `INVALID_REQUEST` | 请求参数不合法 |
| `TASK_NOT_FOUND` | 找不到指定任务 |
| `RESULT_NOT_READY` | 任务结果尚未就绪 |
| `INTERNAL_ERROR` | 未预期的服务端错误 |

## 4. 创建任务

### 4.1 接口信息

`POST /api/tasks`

作用：创建一个新的算子生成与测试任务。

### 4.2 请求参数

请求体：

```json
{
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `operator` | string | 是 | 算子名称，第一阶段为 `vector_add` |
| `description` | string | 否 | 任务描述 |
| `shape` | integer array | 是 | 张量形状，每个维度必须为正整数 |
| `dtype` | string | 否 | 数据类型，默认 `float32` |

第一阶段只接受当前支持范围内的算子和数据类型。

### 4.3 成功响应

HTTP 状态码：`201 Created`

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

说明：

- `task_id` 由 backend 自动生成。
- 初始状态为 `pending`。
- 任务创建后，由 backend 负责后续任务流程。

## 5. 查询任务列表

### 5.1 接口信息

`GET /api/tasks`

作用：获取任务列表。

### 5.2 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `status` | string | 否 | 无 | 按任务状态筛选 |
| `limit` | integer | 否 | 20 | 每页数量，最大 100 |
| `offset` | integer | 否 | 0 | 分页偏移量 |

### 5.3 成功响应

HTTP 状态码：`200 OK`

```json
{
  "items": [
    {
      "task_id": "task_001",
      "operator": "vector_add",
      "description": "计算两个向量对应位置元素之和",
      "shape": [4],
      "dtype": "float32",
      "status": "completed",
      "failure_stage": null,
      "created_at": "2026-11-20T10:00:00Z",
      "updated_at": "2026-11-20T10:00:01Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

说明：

- `items` 为当前页任务列表。
- `total` 为符合筛选条件的任务总数。
- `limit` 为本次查询的最大返回数量。
- `offset` 为本次查询的分页偏移量。

## 6. 查询任务详情

### 6.1 接口信息

`GET /api/tasks/{task_id}`

作用：获取指定任务的详细信息，包括任务基本信息和各阶段执行结果。

### 6.2 成功响应

HTTP 状态码：`200 OK`

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

说明：

1. `task` 保存任务基本信息。
2. `generation` 保存代码生成结果。
3. `execution` 保存执行结果。
4. `evaluation` 保存正确性评估结果。
5. `benchmark` 保存性能评估结果。
6. 如果任务尚未进入某个阶段，对应结果字段可以为 `null`。
7. 如果某个阶段失败，应保留该阶段的错误信息。

任务不存在时：

HTTP 状态码：`404 Not Found`

```json
{
  "detail": {
    "code": "TASK_NOT_FOUND",
    "message": "Task not found"
  }
}
```

## 7. 查询任务结果

### 7.1 接口信息

`GET /api/tasks/{task_id}/result`

作用：获取指定任务的执行结果。

该接口主要供前端结果展示页面使用。

### 7.2 结果尚未就绪

如果任务尚未完成，返回：

HTTP 状态码：`409 Conflict`

```json
{
  "detail": {
    "code": "RESULT_NOT_READY",
    "message": "Task result is not ready"
  }
}
```

### 7.3 成功响应

HTTP 状态码：`200 OK`

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

说明：

任务结果接口和任务详情接口使用相同的结果字段命名，避免前端处理两套不同的数据结构。

## 8. HTTP 状态码汇总

| HTTP 状态码 | 场景 |
|---|---|
| 200 | 查询成功 |
| 201 | 创建任务成功 |
| 400 | 请求参数不合法 |
| 404 | 任务不存在 |
| 409 | 任务结果尚未就绪 |
| 500 | 未预期的服务端错误 |

## 9. 手动接口测试

启动 backend 服务后，可以通过 FastAPI 自动生成的接口文档进行测试：

`http://127.0.0.1:8000/docs`

测试步骤：

1. 找到 `POST /api/tasks`。
2. 输入创建任务的 JSON 请求。
3. 点击 Execute，查看返回的 `task_id`。
4. 找到 `GET /api/tasks/{task_id}`。
5. 输入刚刚获得的 `task_id`，查询任务详情。
6. 找到 `GET /api/tasks/{task_id}/result`。
7. 查询任务执行结果。
8. 检查返回的任务状态、生成代码、执行结果、正确性评估和性能记录。

接口测试需要检查：

- HTTP 状态码是否正确；
- 请求参数校验是否有效；
- 响应字段是否符合数据契约；
- 任务状态是否正确变化；
- 错误信息是否符合统一格式；
- 数据库中的任务记录是否与 API 返回一致。

## 10. API 与共享模型的关系

API 是前端和 backend 之间的通信接口；共享模型是项目内部各模块统一使用的数据结构。

两者应保持一致，但职责不同：

| 内容 | 作用 |
|---|---|
| `contracts/` | 定义项目内部统一的数据模型 |
| `backend/` | 接收 API 请求、校验数据、管理任务流程 |
| `agent/` | 生成算子代码 |
| `executor/` | 执行或模拟执行算子 |
| `evaluator/` | 评估正确性和性能 |
| `storage/` | 保存任务和执行结果 |
| `frontend/` | 调用 API 并展示数据 |

如果修改了共享模型中的字段或类型，需要检查对应 API 请求、响应和相关模块是否也需要调整。
