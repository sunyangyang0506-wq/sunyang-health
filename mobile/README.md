# Sunyang Health Mobile

独立 iOS / Android 健康数字孪生 App。当前版本以 iOS 为首要验证平台，直接接入 Apple HealthKit；Android 预留 Health Connect 接入位。

## 技术栈

- Expo SDK 57 / React Native 0.86
- Expo Dev Client：承载 HealthKit 等原生模块
- Expo SecureStore：本机安全保存会话
- Expo LocalAuthentication：Face ID / Touch ID / 指纹解锁
- `@kingstinct/react-native-healthkit`：iOS HealthKit 原生桥接
- FastAPI：复用仓库现有健康数据管线与报告引擎

## 登录与设备绑定

这是单人私人 App，不依赖微信、短信平台或第三方 OAuth。

1. 后端配置高强度随机 `APP_ENROLLMENT_CODE`。
2. App 首次安装输入配对码。
3. 后端先验证 `APP_SESSION_SECRET`，再原子消费首次绑定状态并返回 30 天会话令牌。
4. 令牌仅保存于 SecureStore。
5. 后续打开 App 优先使用 Face ID / Touch ID 解锁。
6. 默认不允许第二台设备重复绑定；设备更换时由管理员临时设置 `APP_ALLOW_REENROLL=true`，同时轮换配对码，完成后立即关闭。

## 后端环境变量

```bash
HEALTH_SYNC_TOKEN=后台同步专用高强度随机值
APP_ENROLLMENT_CODE=首次设备绑定高强度随机码
APP_SESSION_SECRET=至少32字节随机密钥
HEALTH_DB_PATH=/data/health.db
APP_ALLOW_REENROLL=false
```

不要把以上值提交到 GitHub。生产环境必须给 `/data` 挂持久卷，否则容器重建会丢失 SQLite 数据与首次绑定状态。

## App 环境变量

复制 `.env.example` 为本地环境文件：

```bash
EXPO_PUBLIC_API_BASE=https://your-health-api.example.com
```

API 必须是受信任的公网 HTTPS 地址。

## 后端容器启动

仓库根目录已经提供 `Dockerfile`：

```bash
docker build -t sunyang-health-api .
docker run --rm -p 8000:8000 \
  -v sunyang-health-data:/data \
  -e APP_ENROLLMENT_CODE='replace-me' \
  -e APP_SESSION_SECRET='replace-me' \
  -e HEALTH_SYNC_TOKEN='replace-me' \
  sunyang-health-api
```

上线后先验证：

```text
GET https://<api-domain>/health
=> {"status":"ok"}
```

## iPhone Development Build

HealthKit 属于原生能力，不能使用 Expo Go 完成真实验证。仓库已提供 `eas.json` development profile。

```bash
cd mobile
npm install
npm run typecheck
npx eas build --profile development --platform ios
```

也可在已配置 Apple Development Team 的 Mac 上本地运行：

```bash
npm run prebuild
npm run ios
```

安装 development build 到真实 iPhone 后，通过 Dev Client 启动项目。

## iOS HealthKit 当前读取范围

- Steps
- Active Energy
- Apple Exercise Time
- Walking / Running Distance
- Resting Heart Rate
- HRV (SDNN)
- Weight
- Body Fat Percentage
- Lean Body Mass
- Sleep Analysis

当前只请求读取权限，不主动写入健康数据。

步数、活动能量、运动时长与距离使用 HealthKit Statistics `cumulativeSum` 聚合，避免简单相加 iPhone 与 Apple Watch 多源样本。体重、体脂、去脂体重、HRV 与静息心率保留最近样本时间。

## 当前 App API

### 首次设备绑定

`POST /v1/app/enroll`

```json
{ "enrollment_code": "..." }
```

### App 会话上传 HealthKit 数据

`POST /v1/app/sync/apple-health`

Header:

```text
Authorization: Bearer <session_token>
```

### 拉取今日摘要

`GET /v1/app/summary?record_date=YYYY-MM-DD`

Header:

```text
Authorization: Bearer <session_token>
```

App 使用设备本地日历日期请求摘要，避免服务器时区导致凌晨数据跨日。

## 一键同步流程

首页“授权并同步 Apple Health”按钮会依次完成：

1. 请求 HealthKit 权限。
2. 从本机读取当日累计活动指标、最近生理指标和最近一晚睡眠。
3. 携带 App 会话上传到 `/v1/app/sync/apple-health`。
4. 后端标准化、入库并生成日快照。
5. App 重新请求 `/v1/app/summary`。
6. 刷新恢复状态、睡眠、HRV、静息心率、步数、体重、体脂、去脂体重和今日行动建议。

如果今天没有新的身体组成测量，摘要会回退显示目标日期之前最近一次身体测量；趋势分析仍应使用原始测量日期。

## 全链路验收定义

1. FastAPI 部署到公网 HTTPS，`/health` 返回 OK，并挂载持久卷。
2. iPhone 安装 development build。
3. 输入首次配对码并绑定成功；第二次使用同一配对码默认被拒绝。
4. 会话写入 SecureStore。
5. 重启 App 后 Face ID / Touch ID 解锁成功。
6. Apple Health 权限弹窗出现并可逐项授权。
7. 点击“授权并同步 Apple Health”后，后端接收到真实 HealthKit 数据。
8. `/v1/app/summary` 返回设备本地当天的真实健康摘要。
9. 首页展示睡眠、HRV、静息心率、步数、体重、体脂、去脂体重及行动建议。
10. 会话过期后 App 自动清理本地令牌并要求重新绑定。

## CI

PR 会自动执行：

- Python `unittest` 后端回归测试
- Mobile TypeScript strict typecheck

## 下一步

- 把当前按需同步升级为 HealthKit anchored / background 增量同步。
- 增加 7 / 28 / 90 日趋势图。
- 增加女性生命周期结构化记录。
- 增加本地通知与每日健康建议推送。
- Android 接入 Health Connect。
