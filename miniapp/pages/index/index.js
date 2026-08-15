const demo = require('../../utils/mock')
const app = getApp()

function wxLogin() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (res) => res.code ? resolve(res.code) : reject(new Error('wx.login returned no code')),
      fail: reject
    })
  })
}

function request({ url, method = 'GET', data, token }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method,
      data,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)
        else reject(new Error(`HTTP ${res.statusCode}`))
      },
      fail: reject
    })
  })
}

function metricItems(metrics = {}) {
  const show = (v, digits = 1) => (v === null || v === undefined) ? '--' : Number(v).toFixed(digits)
  return [
    { key: 'sleep', label: '睡眠', value: show(metrics.sleep_hours), unit: 'h', hint: '目标 ≥ 7h' },
    { key: 'hrv', label: 'HRV', value: show(metrics.hrv_ms, 0), unit: 'ms', hint: '对比个人基线' },
    { key: 'rhr', label: '静息心率', value: show(metrics.resting_heart_rate, 0), unit: 'bpm', hint: '关注异常抬升' },
    { key: 'steps', label: '步数', value: metrics.steps == null ? '--' : Number(metrics.steps).toLocaleString(), unit: '', hint: '保持稳定即可' },
    { key: 'weight', label: '体重', value: show(metrics.weight_kg), unit: 'kg', hint: '看 7 日均值' },
    { key: 'fat', label: '体脂', value: show(metrics.body_fat_percent), unit: '%', hint: '趋势优先' }
  ]
}

Page({
  data: {
    tabs: [
      { key: 'today', label: '今日' },
      { key: 'trends', label: '趋势' },
      { key: 'women', label: '女性' },
      { key: 'evidence', label: '证据' }
    ],
    activeTab: 'today',
    meta: demo.meta,
    readiness: demo.readiness,
    metrics: demo.metrics,
    actions: demo.actions,
    trends: demo.trends,
    women: demo.women,
    thyroid: demo.thyroid,
    evidence: demo.evidence
  },

  onLoad() {
    this.loadHealthData()
  },

  switchTab(e) {
    this.setData({ activeTab: e.currentTarget.dataset.key })
  },

  async loadHealthData() {
    const { apiBase, demoMode } = app.globalData
    if (demoMode || !apiBase) {
      this.setData({
        meta: {
          ...demo.meta,
          updatedAt: '演示模式 · 尚未配置真实 API'
        }
      })
      return
    }

    try {
      const code = await wxLogin()
      const auth = await request({
        url: `${apiBase}/v1/auth/wechat`,
        method: 'POST',
        data: { code }
      })
      const token = auth.access_token
      if (!token) throw new Error('missing access token')
      wx.setStorageSync('healthAuthToken', token)
      app.globalData.authToken = token

      const summary = await request({
        url: `${apiBase}/v1/mobile/summary`,
        token
      })

      const level = (summary.readiness && summary.readiness.level) || 'yellow'
      this.setData({
        meta: {
          updatedAt: `真实数据 · ${summary.record_date || '今日'}`,
          privacy: '已通过微信登录态访问受保护健康摘要'
        },
        readiness: {
          level: `${level.charAt(0).toUpperCase()}${level.slice(1)} Day`,
          score: demo.readiness.score,
          summary: (summary.readiness && summary.readiness.summary) || '按已同步数据生成',
          reasons: (summary.readiness && summary.readiness.reasons) || []
        },
        metrics: metricItems(summary.metrics),
        actions: summary.actions && summary.actions.length ? summary.actions : demo.actions
      })
    } catch (err) {
      console.error('health API login/load failed', err)
      this.setData({
        meta: {
          updatedAt: '真实连接失败 · 当前显示演示数据',
          privacy: '未获取到真实健康数据'
        }
      })
      wx.showToast({ title: '微信登录或数据连接失败', icon: 'none' })
    }
  },

  async onPullDownRefresh() {
    await this.loadHealthData()
    wx.stopPullDownRefresh()
  }
})
