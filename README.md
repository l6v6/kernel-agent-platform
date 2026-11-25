# kernel-agent-platform

## 组员 B：第一阶段模拟生成模块

环境：Python 3.11.x、Pydantic v2。生成器不需要模型 API、GPU 或数据库。

在项目根目录执行（Windows PowerShell）：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m examples.generator_demo
```

如果使用 Conda 创建 `.venv`，解释器位于 `.\.venv\python.exe`，请相应替换上述路径。

接口、错误处理、模拟失败测试及交付说明见 [生成模块说明](docs/generator.md)。
本仓库当前仅提供共享模型和生成模块，完整后端、执行器和页面仍待集成。
