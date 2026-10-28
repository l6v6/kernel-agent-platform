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
