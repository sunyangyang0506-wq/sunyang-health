import pandas as pd
import streamlit as st

from app.agent.health_agent import HealthAgent
from app.analytics.data_quality import evaluate_coverage
from app.analytics.trend_engine import build_7_14_30_trends
from app.repository.health_repository import HealthRepository

st.set_page_config(page_title="Personal Health Twin", layout="wide")

repo = HealthRepository()
repo.upsert_demo_snapshot()
agent = HealthAgent()

body = repo.latest_body() or {}
activity = repo.latest_activity() or {}
sleep = repo.latest_sleep() or {}
nutrition = repo.latest_nutrition() or {}

snapshot = {
    "body_fat_percent": body.get("body_fat_percent"),
    "steps": activity.get("steps"),
    "hrv_ms": activity.get("hrv_ms"),
    "resting_heart_rate": activity.get("resting_heart_rate"),
    "sleep_hours": sleep.get("total_sleep_hours"),
    "protein_g": nutrition.get("protein_g"),
}

decision = agent.decide(snapshot)

st.title("Personal Health Digital Twin")
st.caption("生活方式管理演示版，不替代医疗诊断或治疗。")

c1, c2, c3, c4 = st.columns(4)
c1.metric("体重", f"{body.get('weight_kg', '--')} kg")
c2.metric("体脂率", f"{body.get('body_fat_percent', '--')} %")
c3.metric("步数", f"{activity.get('steps', '--')}")
c4.metric("睡眠", f"{sleep.get('total_sleep_hours', '--')} h")

c5, c6, c7, c8 = st.columns(4)
c5.metric("HRV", f"{activity.get('hrv_ms', '--')} ms")
c6.metric("静息心率", f"{activity.get('resting_heart_rate', '--')} bpm")
c7.metric("蛋白质", f"{nutrition.get('protein_g', '--')} g")
c8.metric("今日模式", decision.mode)

st.subheader("今日优先级")
for item in decision.priorities:
    st.write(f"- {item}")

st.subheader("今日行动")
for item in decision.actions:
    st.write(f"- {item}")

if decision.cautions:
    st.subheader("安全提示")
    for item in decision.cautions:
        st.warning(item)

history = repo.body_history(30)
if history:
    df = pd.DataFrame(history)
    if "record_date" in df.columns:
        df["record_date"] = pd.to_datetime(df["record_date"])
        df = df.sort_values("record_date").set_index("record_date")
        trend_cols = [c for c in ["weight_kg", "body_fat_percent", "muscle_mass_kg"] if c in df.columns]
        if trend_cols:
            st.subheader("身体趋势")
            st.line_chart(df[trend_cols])

        st.subheader("7 / 14 / 30 天趋势摘要")
        summary_rows = []
        for metric, tolerance in [("weight_kg", 0.3), ("body_fat_percent", 0.5)]:
            if metric not in df.columns:
                continue
            values = [v for v in df[metric].tolist() if pd.notna(v)]
            trends = build_7_14_30_trends(values, tolerance=tolerance)
            for days, trend in trends.items():
                summary_rows.append({
                    "指标": metric,
                    "窗口": f"{days}天",
                    "均值": trend.average,
                    "变化": trend.change,
                    "方向": trend.direction,
                    "样本数": len(trend.values),
                })
        if summary_rows:
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

st.subheader("数据质量")
quality_rows = []
for name, record, expected_days in [
    ("身体", body, 14),
    ("运动", activity, 7),
    ("睡眠", sleep, 7),
    ("营养", nutrition, 7),
]:
    source = record.get("source", "missing") if record else "missing"
    confidence = record.get("confidence", "unknown") if record else "unknown"
    days_with_data = 1 if record else 0
    coverage, sufficient = evaluate_coverage(days_with_data, expected_days)
    quality_rows.append({
        "类别": name,
        "来源": source,
        "可信度": confidence,
        "估算覆盖率": round(coverage, 2),
        "足够用于趋势": sufficient,
    })

st.dataframe(pd.DataFrame(quality_rows), use_container_width=True)
st.info("当前覆盖率仅用于演示；V0.2 将以真实 Apple Health 同步天数计算。")
