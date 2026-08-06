# Personal Health Digital Twin AI

个人健康数字孪生智能体。

## Vision
融合 Apple Health、身体指标、运动、睡眠、饮食数据，通过数据治理、趋势分析与 Health Agent 生成每日健康决策。

## V0.2 Architecture

```text
Apple Health / HealthKit / Shortcut / Export JSON
                 |
                 v
       Apple Health Connector
       - metric mapping
       - unit normalization
                 |
                 v
        Data Quality Engine
       - completeness
       - conflict detection
       - confidence downgrade
                 |
                 v
          Ingestion Pipeline
                 |
                 v
              SQLite
     body / activity / sleep
        nutrition / snapshots
                 |
          +------+------+
          |             |
          v             v
    Trend Engine     Health Agent
     7/14/30d            |
          +------+------+
                 v
       Streamlit Dashboard
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/dashboard/dashboard.py
```

## Import Apple Health data
The repository cannot directly bypass iOS HealthKit permissions. Use an iOS HealthKit client, Shortcut/export workflow, or another authorized bridge to produce a JSON array using this neutral contract:

```json
[
  {
    "type": "HKQuantityTypeIdentifierStepCount",
    "value": 8432,
    "unit": "count",
    "start_date": "2026-08-07T06:30:00+08:00",
    "source": "Apple Watch"
  }
]
```

Then run:

```bash
python scripts/import_apple_health.py data/raw/apple_health.json
```

The pipeline normalizes supported HealthKit identifiers, converts units, detects same-day conflicts, writes body/activity/sleep records, and creates one `daily_snapshots` record per date.

## Supported Apple Health metrics
- weight, BMI, body fat, lean body mass
- steps, active energy, exercise minutes, walking/running distance
- resting heart rate, HRV, VO2 max
- sleep duration

## Data governance rules
- every normalized record retains date/time and source
- latest valid record is used for a daily metric snapshot
- material same-day conflicts are flagged instead of silently resolved
- body records with detected conflicts are downgraded to confidence E
- medical/lab data should remain a higher-priority source than consumer-device estimates when those modules are added
- missing data is represented as missing; it is never fabricated

## Dashboard
The Streamlit dashboard shows current metrics, Health Agent actions, body trends, 7/14/30-day trend summaries, source/confidence information and basic coverage indicators.

## Safety Boundary
This system supports lifestyle management and longitudinal data organization. It does not diagnose disease, change medication doses, infer a diagnosis from a wearable reading, or replace medical review.

## Version status

### V0.1 completed
- data models
- analytics engine
- SQLite store
- repository layer
- rule-first Health Agent
- Streamlit dashboard

### V0.2 completed in code
- Apple Health neutral connector
- metric/unit normalization
- ingestion pipeline
- daily health snapshot persistence
- data quality and conflict detection
- 7/14/30-day trend engine
- dashboard trend/quality integration
- JSON import CLI

### Remaining deployment boundary
Actual automatic iPhone-to-server delivery requires an authorized iOS HealthKit/Shortcut bridge and a running deployment target. GitHub code alone cannot read private Apple Health data from the phone.

### V1.0 next
- authenticated sync API
- medical/lab and medication context
- menstrual/recovery context
- daily/weekly report generator
- personalized decision rules and alert governance
