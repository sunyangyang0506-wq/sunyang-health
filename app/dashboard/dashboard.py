import pandas as pd
import streamlit as st

from app.agent.health_agent import HealthAgent
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
        df = df.set_index("record_date")
        trend_cols = [c for c in ["weight_kg", "body_fat_percent", "muscle_mass_kg"] if c in df.columns]
        if trend_cols:
            st.subheader("身体趋势")
            st.line_chart(df[trend_cols])

st.subheader("数据质量")
st.write({
    "身体数据来源": body.get("source", "missing"),
    "身体数据可信度": body.get("confidence", "unknown"),
    "运动数据来源": activity.get("source", "missing"),
    "睡眠数据来源": sleep.get("source", "missing"),
    "营养数据来源": nutrition.get("source", "missing"),
})
