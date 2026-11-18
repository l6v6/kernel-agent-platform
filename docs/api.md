# API 接口文档

- 前缀：`/api`
- 数据格式：JSON
- 第一阶段算子：`vector_add`

## 1. 统一任务状态
`pending`、`generating`、`generated`、`running`、`evaluating`、`completed`、`failed`。

失败阶段代码通过 `failure_stage` 表示：`generation_failed`、`execution_failed`、`evaluation_failed`。注意：它们不是新的任务状态，任务状态仍为 `failed`。

通用错误格式：

```json
{
  "detail": {
    "code": "INVALID_REQUEST",
    "message": "shape must contain positive integers"
  }
}
```

## 2. 创建任务

`POST /api/tasks`

请求：

```json
{
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32"
}
```

字段：`operator` string 必填；`description` string 可选；`shape` 正整数数组必填；`dtype` string 必填，第一阶段支持 `float32`。

成功响应：HTTP 201

```json
{
  "task_id": "task_001",
  "operator": "vector_add",
  "status": "pending",
  "created_at": "2026-11-18T10:00:00Z"
}
```

## 3. 查询任务列表

`GET /api/tasks`

可选参数：`status`、`limit`（默认 20，最大 100）、`offset`（默认 0）。

```json
{
  "items": [
    {
      "task_id": "task_001",
      "operator": "vector_add",
      "status": "completed",
      "created_at": "2026-11-18T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## 4. 查询任务详情

`GET /api/tasks/{task_id}`

```json
{
  "task_id": "task_001",
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32",
  "status": "completed",
  "failure_stage": null,
  "error": null,
  "generation": {
    "success": true,
    "language": "python",
    "code": "def vector_add(a, b): return a + b"
  },
  "execution": {
    "success": true,
    "output": [6, 8, 10, 12]
  },
  "evaluation": {
    "passed": true,
    "message": "结果一致"
  },
  "benchmark": {
    "latency_ms": 0.01,
    "is_simulated": true,
    "note": "模拟记录，不代表真实 GPU 性能"
  },
  "created_at": "2026-11-18T10:00:00Z",
  "updated_at": "2026-11-18T10:00:01Z"
}
```

以上时间、task_id 和 latency 均为格式示例，不是真实数据。

任务不存在：HTTP 404，错误码 `TASK_NOT_FOUND`。

## 5. 查询任务结果

`GET /api/tasks/{task_id}/result`

任务尚未完成时返回 HTTP 409，错误码 `RESULT_NOT_READY`。

完成后的示例：

```json
{
  "task_id": "task_001",
  "status": "completed",
  "correctness": {
    "passed": true,
    "expected": [6, 8, 10, 12],
    "actual": [6, 8, 10, 12],
    "message": "结果一致"
  },
  "performance": {
    "latency_ms": 0.01,
    "is_simulated": true,
    "note": "模拟记录，不代表真实 GPU 性能"
  }
}
```

## 6. HTTP 状态码

| HTTP | 场景 |
|---|---|
| 200 | 查询成功 |
| 201 | 创建成功 |
| 400 | 参数不合法 |
| 404 | 任务不存在 |
| 409 | 结果尚未就绪 |
| 500 | 未预期服务端错误 |

## 7. 手动接口测试
启动服务后访问 `/docs`：
1. 在 `POST /api/tasks` 输入创建任务 JSON 并执行。
2. 复制返回的 `task_id`。
3. 在 `GET /api/tasks/{task_id}` 查询详情。
4. 在 `GET /api/tasks/{task_id}/result` 查询结果。

接口测试就是模拟前端发送 HTTP 请求，检查状态码、响应字段、错误处理和数据库结果。
