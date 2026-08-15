module.exports = {
  meta: {
    updatedAt: '演示数据 · 未连接真实健康记录',
    privacy: '公开仓库仅包含字段结构和示例值'
  },
  readiness: {
    level: 'Yellow Day',
    score: 72,
    summary: '恢复尚可，适合低冲击有氧 + 轻力量，不追求高强度。',
    reasons: ['睡眠接近目标', 'HRV 接近个人基线', '近期活动量波动较大']
  },
  metrics: [
    { key: 'sleep', label: '睡眠', value: '7.1', unit: 'h', hint: '目标 ≥ 7h' },
    { key: 'hrv', label: 'HRV', value: '35', unit: 'ms', hint: '对比 28 日基线' },
    { key: 'rhr', label: '静息心率', value: '65', unit: 'bpm', hint: '关注异常抬升' },
    { key: 'steps', label: '步数', value: '8,300', unit: '', hint: '保持稳定即可' },
    { key: 'weight', label: '体重', value: '70.0', unit: 'kg', hint: '看 7 日均值' },
    { key: 'fat', label: '体脂', value: '31.8', unit: '%', hint: '趋势优先' }
  ],
  actions: [
    '30–40 分钟快走 / 椭圆机 / 单车，保持可完整说话的强度',
    '10–20 分钟力量训练，优先下肢髋主导、推、拉、核心',
    '三餐优先蛋白质，避免通过跳餐制造过大热量缺口',
    '每 90 分钟离屏活动 5 分钟，晚间提前 30 分钟降认知负荷'
  ],
  trends: [
    { label: '睡眠', value: 78, note: '近 7 天数据完整度不足时不判定趋势' },
    { label: 'HRV', value: 64, note: '只和个人基线比较' },
    { label: '活动', value: 82, note: '避免单日暴增' },
    { label: '体脂', value: 46, note: '关注 4–8 周缓慢下降' }
  ],
  women: {
    stage: '生命周期状态：待用户确认',
    cycle: '月经/周期数据：待连接',
    symptomItems: ['经期与流量', '潮热/夜汗', '情绪波动', '睡眠受扰', '训练表现', '主观精力'],
    note: '周期是解释变量，不单独决定训练强度。'
  },
  thyroid: {
    title: '甲状腺术后管理',
    items: ['用药按既定医嘱执行', '不依据体重或单日疲劳自行调整剂量', '实验室与影像随访作为高优先级医疗数据源']
  },
  evidence: [
    { level: 'E1', title: '随机试验 / 系统综述', rule: '可直接影响算法，但需匹配适用人群' },
    { level: 'E2', title: '大型观察研究', rule: '进入风险权重，不直接生成绝对训练禁令' },
    { level: 'E3', title: '立场文件 / 机制综述', rule: '用于解释和边界设计' },
    { level: 'E4', title: '专家公开观点', rule: '只作为启发，不等于已被临床验证' }
  ]
}
