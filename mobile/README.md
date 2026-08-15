# Sunyang Health Mobile

独立 iOS / Android 健康数字孪生 App。当前版本以 iOS 为首要验证平台，直接接入 Apple HealthKit；Android 预留 Health Connect 接入位。

## 技术栈

- Expo SDK 57 / React Native 0.86
- Expo SecureStore：本机安全保存会话
- Expo LocalAuthentication：Face ID / Touch ID / 指纹解锁
- `@kingstinct/react-native-healthkit`：iOS HealthKit 原生桥接
- FastAPI：复用仓库现有健康数据管线与报告引擎

## 登录方式

这是单人私人 App，不依赖微信、短信平台或第三方 OAuth。

1. 后端配置一次性 `APP_ENROLLMENT_CODE`。
2. App 首次安装输入配对码。
3. 后端返回 30 天会话令牌。
4. 令牌仅保存于 SecureStore。
5. 后续打开 App 优先使用 Face ID / Touch ID 解锁。

生产环境建议在首次绑定成功后立即轮换 `APP_ENROLLMENT_CODE`。

## 后端环境变量

```bash
HEALTH_SYNC_TOKEN=...
APP_ENROLLMENT_CODE=一次性高强度随机码
APP_SESSION_SECRET=至少32字节随机密钥
```

不要把以上值提交到 GitHub。

## App 环境变量

复制 `.env.example` 为 `.env.local`：

```bash
EXPO_PUBLIC_API_BASE=https://your-health-api.example.com
```

## 本地启动

```bash
cd mobile
npm install
npx expo prebuild
npx expo run:ios
```

HealthKit 属于原生能力，不能只用 Expo Go 完成真实验证。需要生成原生开发构建，并在 iPhone 上授权 HealthKit 数据类型。

## iOS HealthKit 当前请求范围

- Steps
- Heart Rate
- Resting Heart Rate
- HRV (SDNN)
- Weight
- Body Fat Percentage
- Sleep Analysis

当前只请求读取权限，不主动写入健康数据。

## 当前 API

### 首次设备绑定

`POST /v1/app/enroll`

```json
{ "enrollment_code": "..." }
```

### 拉取今日摘要

`GET /v1/app/summary`

Header:

```text
Authorization: Bearer <session_token>
```

## 全链路验收定义

1. iPhone 安装开发构建。
2. 输入一次性配对码并绑定成功。
3. 会话写入 SecureStore。
4. 重启 App 后 Face ID / Touch ID 解锁成功。
5. Apple Health 权限弹窗出现并可逐项授权。
6. FastAPI `/v1/app/summary` 返回当日真实健康摘要。
7. 首页展示睡眠、HRV、静息心率、步数、体重、体脂及行动建议。
8. 会话过期后 App 自动清理本地令牌并要求重新绑定。

## 下一步

- 用 HealthKit anchored queries 将 iPhone 新增数据直接同步到 `/v1/sync/apple-health`。
- 增加 7 / 28 / 90 日趋势图。
- 增加女性生命周期结构化记录。
- 增加本地通知与每日健康建议推送。
- Android 接入 Health Connect。
