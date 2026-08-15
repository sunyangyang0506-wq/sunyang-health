let runtimeConfig = {
  apiBase: '',
  demoMode: true
}

try {
  runtimeConfig = require('./env')
} catch (err) {
  // Production/local env.js is intentionally not committed.
}

App({
  globalData: {
    apiBase: runtimeConfig.apiBase || '',
    demoMode: runtimeConfig.demoMode !== false,
    authToken: wx.getStorageSync('healthAuthToken') || ''
  }
})
