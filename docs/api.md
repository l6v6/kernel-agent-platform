# API 接口约定

> 文档状态：初始草案。接口路径、字段和状态码以实际实现为准。

## 1. 通用约定

- 基础路径建议：`/api`
- 数据格式：JSON
- 字符编码：UTF-8
- 每个任务由唯一 `task_id` 标识。
- 长耗时任务采用“提交任务后返回 ID，再查询状态”的方式，不让创建请求无限等待。

## 2. 创建任务

`POST /api/tasks`

请求示例：

```json
{
  "operator": "relu",
  "input_shape": [1024],
  "dtype": "float32",
  "backend": "triton"
}
```

字段说明：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `operator` | string | 是 | 已支持的算子名称 |
| `input_shape` | integer array | 是 | 输入张量形状，需校验正负值和上限 |
| `dtype` | string | 是 | 已支持的数据类型 |
| `backend` | string | 是 | 已配置且可用的执行后端 |

成功响应示例：

```json
{
  "task_id": "task_example",
  "status": "pending"
}
```

## 3. 查询任务

`GET /api/tasks/{task_id}`

响应示例：

```json
{
  "task_id": "task_example",
  "status": "testing",
  "created_at": "YYYY-MM-DDTHH:mm:ssZ"
}
```

## 4. 查询任务结果

`GET /api/tasks/{task_id}/result`

响应示例：

```json
{
  "task_id": "task_example",
  "status": "completed",
  "correctness": {
    "passed": true,
    "details": "由测试程序生成的摘要"
  },
  "performance": {
    "baseline_latency_us": 0.0,
    "candidate_latency_us": 0.0,
    "speedup": 0.0
  }
}
```

上面的性能数值为占位示例，不是实际实验结果。正式响应中应使用真实测量值；若没有有效结果，应返回 `null` 或明确的不可用状态，而不是填入虚构数字。

## 5. 查询任务列表

`GET /api/tasks`

初期可返回最近创建的任务。后续可增加分页、状态筛选和时间范围筛选。

## 6. 错误响应建议

```json
{
  "error": {
    "code": "INVALID_TASK",
    "message": "任务参数无效"
  }
}
```

建议区分参数错误、任务不存在、模型调用失败、编译失败、正确性失败、执行超时和内部错误。不要把详细服务器堆栈或密钥返回给前端。

## 7. 任务状态建议

`pending`、`generating`、`compiling`、`testing`、`benchmarking`、`completed`、`failed`、`timeout`。

## 8. 接口变更流程

1. 在 Issue 或讨论中说明变更原因。
2. 更新本文件和相关数据模型。
3. 同步修改后端、前端和测试。
4. 通过 Pull Request 评审后合并。

## 9. 待确认事项

- [ ] 是否使用 `/api/v1` 作为版本前缀
- [ ] 任务状态采用轮询还是其他通知方式
- [ ] 分页、鉴权和错误码的最终规范
- [ ] 实际支持的算子、后端和数据类型
