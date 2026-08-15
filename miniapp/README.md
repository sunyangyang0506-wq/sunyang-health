# 女性健康数字孪生小程序（MVP）

这是 `sunyang-health` 的微信小程序展示层原型，目标是把健康数字孪生从 Streamlit 桌面看板扩展到移动端日常使用。

## 当前展示模块

- 今日：Readiness、睡眠、HRV、静息心率、步数、体重、体脂、当天行动建议
- 趋势：睡眠、HRV、活动、体脂的趋势与数据质量提示
- 女性：女性生命周期状态、经期/围绝经期症状字段、甲状腺术后管理边界
- 证据：Stacy Sims 研究证据分层 E1–E4

## 隐私边界

本仓库为公开仓库，因此本目录只存放：

- UI 结构
- 字段定义
- 演示数据
- 决策规则说明

**不得提交真实的个人健康记录、病史、药物、化验单、周期记录或 Apple Health 原始数据。**

生产环境应通过受认证的 HTTPS API 获取用户授权后的数据，并将身份信息与健康数据隔离存储。

## 本地预览

1. 安装微信开发者工具。
2. 导入项目时将目录选择为本仓库的 `miniapp/`。
3. 当前 `project.config.json` 使用 `touristappid`，用于原型预览。
4. 页面默认读取 `utils/mock.js`，不依赖后端即可展示。

## 计划中的后端契约

建议后端提供：

`GET /api/v1/mobile/summary`

返回结构示例：

```json
{
  "readiness": {
    "level": "yellow",
    "score": 72,
    "summary": "恢复尚可，适合低冲击有氧 + 轻力量",
    "reasons": []
  },
  "metrics": {
    "sleep_hours": 7.1,
    "hrv_ms": 35,
    "resting_heart_rate": 65,
    "steps": 8300,
    "weight_kg": 70.0,
    "body_fat_percent": 31.8,
    "lean_mass_kg": 48.0
  },
  "actions": [],
  "data_quality": {
    "sleep": "sufficient",
    "hrv": "sufficient",
    "body": "sufficient"
  }
}
```

## 决策原则

小程序只展示已经过后端规则引擎计算的结果，不在前端直接完成医学判断。

推荐后端逻辑：

1. 先判断数据完整性，数据不足时降低结论置信度。
2. HRV 只与个人 28 日基线比较，不使用通用“正常值”。
3. 月经周期/激素状态作为解释变量，而非单独训练开关。
4. 当天 Readiness 综合睡眠、HRV、静息心率、主观精力、女性症状和训练负荷。
5. 体脂下降同时要求去脂体重保持稳定，避免把掉肌肉误判为减脂成功。
6. 医疗数据（化验、影像、医嘱）优先于消费级可穿戴设备估算。

## 下一步

- 接入 `sunyang-health` 的 API 层
- 用户鉴权与 token 管理
- 女性生命周期 / 月经 / 围绝经期结构化记录
- 甲状腺随访数据页（仅记录，不自动改药）
- 7/28/90 天趋势图
- 数据质量与异常值提示
- 每日 Green / Yellow / Red Day 决策
