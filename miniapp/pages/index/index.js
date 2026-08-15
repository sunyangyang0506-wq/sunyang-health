const demo = require('../../utils/mock')

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

  switchTab(e) {
    this.setData({ activeTab: e.currentTarget.dataset.key })
  },

  onPullDownRefresh() {
    wx.stopPullDownRefresh()
    wx.showToast({
      title: '当前为演示数据',
      icon: 'none'
    })
  }
})
