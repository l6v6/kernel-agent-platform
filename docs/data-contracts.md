# 模块数据契约说明

## 1. 数据结构是什么
数据结构约定模块传递的数据有哪些字段、字段类型、含义和是否必填，相当于模块之间的交接单。先约定数据契约，再确定函数签名，再分别实现模块。

## 2. Task（任务对象）

```json
{
  "task_id": "task_001",
  "operator": "vector_add",
  "description": "计算两个向量对应位置元素之和",
  "shape": [4],
  "dtype": "float32"
}
```

| 字段 | 类型 | 含义 |
|---|---|---|
| task_id | string | 唯一编号 |
| operator | string | 算子名称 |
| description | string/null | 任务描述 |
| shape | integer[] | 张量形状 |
| dtype | string | 数据类型 |

## 3. 生成模块 GenerationResult
函数：`generate(task) -> GenerationResult`

成功：

```json
{
  "success": true,
  "code": "def vector_add(a, b): return a + b",
  "language": "python",
  "error": null
}
```

失败：

```json
{
  "success": false,
  "code": null,
  "language": "python",
  "error": {
    "code": "GENERATION_ERROR",
    "message": "mock generation failed"
  }
}
```

## 4. 执行模块 ExecutionResult
函数：`run(task, generation_result, test_case) -> ExecutionResult`

成功：

```json
{
  "success": true,
  "output": [6, 8, 10, 12],
  "error": null
}
```

失败：

```json
{
  "success": false,
  "output": null,
  "error": {
    "code": "EXECUTION_ERROR",
    "message": "mock execution failed"
  }
}
```

第一阶段执行器只返回受控模拟结果，不执行任意生成代码。

## 5. 正确性评估 EvaluationResult
函数：`evaluate(expected, actual, tolerance) -> EvaluationResult`

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

第一阶段先检查长度/形状一致，再检查对应元素绝对误差是否不超过容差。

## 6. 性能评估 BenchmarkResult
函数：`measure(...) -> BenchmarkResult`

```json
{
  "latency_ms": 0.01,
  "is_simulated": true,
  "measurement_method": "mock",
  "note": "模拟记录，不代表真实 GPU 性能"
}
```

数值仅为格式示例。后续真实 GPU 阶段再加入设备型号、预热次数、测量次数和统计值。

## 7. 统一 TaskResult

```json
{
  "task_id": "task_001",
  "status": "completed",
  "failure_stage": null,
  "generation": {},
  "execution": {},
  "evaluation": {},
  "benchmark": {}
}
```

## 8. 数据契约与代码的关系
1. 本文确定字段、类型和含义。
2. 在 `backend/schemas.py` 中用 Pydantic 定义 API 数据模型。
3. 各模块按契约确定函数签名和返回对象。
4. 每个模块编写成功和失败测试。
5. 集成时检查上游输出能否直接作为下游输入。
