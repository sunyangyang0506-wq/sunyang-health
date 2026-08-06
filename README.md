# Personal Health Digital Twin AI

个人健康数字孪生智能体。

## Vision

融合 Apple Health、身体指标、运动、睡眠、饮食数据，通过 AI Agent 生成每日健康决策。

## Architecture

Data Source -> Health Data Model -> Analytics Engine -> AI Health Agent -> Dashboard

## MVP Modules

- Body Metrics
- Activity Metrics
- Sleep Metrics
- Nutrition Metrics
- Health Scoring
- SQLite Health Data Store
- Rule-first Health Agent
- Streamlit Dashboard

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/dashboard/dashboard.py
```

首次启动时，如果本地数据库为空，会写入一组 `demo` 数据用于验证 Dashboard。真实数据接入后应停用 demo seed，并以来源、日期、可信度和冲突状态为准。

## Current Data Flow

```text
Body / Activity / Sleep / Nutrition
            |
            v
        SQLite Store
            |
            v
      Repository Layer
            |
            v
       Health Agent
            |
            v
    Streamlit Dashboard
```

## Safety Boundary

系统当前只用于生活方式管理与数据整合展示，不用于疾病诊断，不修改药物剂量，不以单次可穿戴设备异常值直接做医学结论。

## Roadmap

### V0.1
- Data model
- Analytics engine
- SQLite store
- Repository layer
- Rule-first Health Agent
- Streamlit dashboard

### V0.2
- Apple Health connector
- Automated daily sync
- Data quality / conflict resolution
- 7 / 14 / 30 day trend windows

### V1.0
- Personal Health OS
- AI health coach
- Lab / medication context integration
- Daily and weekly health reports
