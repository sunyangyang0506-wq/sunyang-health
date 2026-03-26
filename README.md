# sunyang-health

本仓库包含《AI 健身决策助手》的产品文档与 MVP 规则引擎实现。

## 文档

- 产品落地方案：`docs/ai-fitness-decision-assistant-v1.md`

## 代码结构

- `src/fitness_ai/models.py`：核心数据结构与枚举
- `src/fitness_ai/decision_engine.py`：训练/恢复/饮食建议规则引擎
- `src/fitness_ai/human_engine.py`：人感表达适配引擎
- `src/fitness_ai/service.py`：组合服务层（用于首页/AI 教练调用）
- `tests/`：单元测试

## 运行测试

```bash
PYTHONPATH=src pytest -q
```
