import { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

import { enroll, getSummary, HealthSummary } from './src/api';
import { connectHealthData } from './src/healthkit';

const SESSION_KEY = 'sunyang_health_session';
const tabs = ['今日', '趋势', '女性', '证据'] as const;
type Tab = (typeof tabs)[number];

export default function App() {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [enrollmentCode, setEnrollmentCode] = useState('');
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('今日');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    try {
      const token = await SecureStore.getItemAsync(SESSION_KEY);
      if (!token) return;

      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      if (hasHardware && enrolled) {
        const auth = await LocalAuthentication.authenticateAsync({
          promptMessage: '解锁个人健康数据',
          cancelLabel: '取消',
          disableDeviceFallback: false,
        });
        if (!auth.success) return;
      }

      setSessionToken(token);
      await refreshSummary(token);
    } finally {
      setLoading(false);
    }
  }

  async function handleEnroll() {
    if (!enrollmentCode.trim()) {
      Alert.alert('请输入一次性配对码');
      return;
    }
    setLoading(true);
    try {
      const token = await enroll(enrollmentCode);
      await SecureStore.setItemAsync(SESSION_KEY, token, {
        keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
      });
      setSessionToken(token);
      setEnrollmentCode('');
      await refreshSummary(token);
    } catch (error) {
      Alert.alert('配对失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setLoading(false);
    }
  }

  async function refreshSummary(token = sessionToken) {
    if (!token) return;
    setMessage('');
    try {
      const next = await getSummary(token);
      setSummary(next);
    } catch (error) {
      const text = error instanceof Error ? error.message : '加载失败';
      if (text === 'SESSION_EXPIRED') {
        await SecureStore.deleteItemAsync(SESSION_KEY);
        setSessionToken(null);
        setSummary(null);
        Alert.alert('登录已过期', '请重新输入配对码完成设备绑定。');
      } else {
        setMessage(text);
      }
    }
  }

  async function handleConnectHealth() {
    try {
      const result = await connectHealthData();
      Alert.alert(Platform.OS === 'ios' ? 'Apple Health' : '健康数据', result);
    } catch (error) {
      Alert.alert('授权失败', error instanceof Error ? error.message : '未知错误');
    }
  }

  async function signOut() {
    await SecureStore.deleteItemAsync(SESSION_KEY);
    setSessionToken(null);
    setSummary(null);
  }

  const readiness = summary?.readiness;
  const metrics = summary?.metrics || {};
  const metricsList = useMemo(
    () => [
      ['睡眠', metrics.sleep_hours, 'h'],
      ['HRV', metrics.hrv_ms, 'ms'],
      ['静息心率', metrics.resting_heart_rate, 'bpm'],
      ['步数', metrics.steps, ''],
      ['体重', metrics.weight_kg, 'kg'],
      ['体脂', metrics.body_fat_percent, '%'],
    ],
    [metrics]
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" />
        <Text style={styles.muted}>正在准备你的健康数据…</Text>
      </SafeAreaView>
    );
  }

  if (!sessionToken) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.loginCard}>
          <Text style={styles.eyebrow}>SUNYANG HEALTH</Text>
          <Text style={styles.title}>个人健康数字孪生</Text>
          <Text style={styles.body}>
            首次安装只需要输入服务端生成的一次性配对码。成功后，会话安全保存在本机；后续可使用 Face ID / Touch ID 解锁。
          </Text>
          <TextInput
            value={enrollmentCode}
            onChangeText={setEnrollmentCode}
            placeholder="一次性配对码"
            secureTextEntry
            autoCapitalize="none"
            style={styles.input}
          />
          <Pressable style={styles.primaryButton} onPress={handleEnroll}>
            <Text style={styles.primaryButtonText}>绑定此设备</Text>
          </Pressable>
          <Text style={styles.caption}>不使用微信账号，不在 App 内保存后台管理密钥。</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <View>
          <Text style={styles.eyebrow}>SUNYANG HEALTH</Text>
          <Text style={styles.headerTitle}>健康数字孪生</Text>
        </View>
        <Pressable onPress={signOut}>
          <Text style={styles.link}>退出</Text>
        </Pressable>
      </View>

      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <Pressable
            key={tab}
            onPress={() => setActiveTab(tab)}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
          </Pressable>
        ))}
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {activeTab === '今日' && (
          <>
            <View style={styles.heroCard}>
              <Text style={styles.heroLabel}>{readiness?.level || '数据待同步'}</Text>
              <Text style={styles.heroScore}>{readiness?.score ?? '—'}</Text>
              <Text style={styles.body}>{readiness?.summary || '连接数据后生成今日恢复与训练建议。'}</Text>
            </View>

            <View style={styles.grid}>
              {metricsList.map(([label, value, unit]) => (
                <View style={styles.metricCard} key={String(label)}>
                  <Text style={styles.metricLabel}>{String(label)}</Text>
                  <Text style={styles.metricValue}>
                    {value === null || value === undefined ? '—' : String(value)}
                    {value !== null && value !== undefined && unit ? ` ${unit}` : ''}
                  </Text>
                </View>
              ))}
            </View>

            <Section title="今日行动">
              {(summary?.actions || ['等待后端生成个体化建议']).map((item) => (
                <Text style={styles.listItem} key={item}>• {item}</Text>
              ))}
            </Section>

            <Pressable style={styles.secondaryButton} onPress={handleConnectHealth}>
              <Text style={styles.secondaryButtonText}>
                {Platform.OS === 'ios' ? '连接 Apple Health' : '连接健康数据'}
              </Text>
            </Pressable>
            <Pressable style={styles.secondaryButton} onPress={() => void refreshSummary()}>
              <Text style={styles.secondaryButtonText}>刷新数据</Text>
            </Pressable>
            {!!message && <Text style={styles.warning}>{message}</Text>}
          </>
        )}

        {activeTab === '趋势' && (
          <Section title="趋势分析">
            <Text style={styles.body}>下一步接入 7 / 28 / 90 日睡眠、HRV、静息心率、活动量、体重、体脂和去脂体重趋势。</Text>
            <Text style={styles.caption}>趋势判断优先使用个人基线；数据覆盖不足时不输出确定性结论。</Text>
          </Section>
        )}

        {activeTab === '女性' && (
          <Section title="女性生命周期">
            <Text style={styles.listItem}>• 周期/激素状态作为解释变量，而不是单独训练开关。</Text>
            <Text style={styles.listItem}>• 记录睡眠、情绪、潮热/夜汗、主观精力与训练表现。</Text>
            <Text style={styles.listItem}>• 医疗随访数据高于消费级可穿戴设备估算。</Text>
          </Section>
        )}

        {activeTab === '证据' && (
          <Section title="证据引擎">
            <Text style={styles.listItem}>E1 · 随机试验 / 系统综述</Text>
            <Text style={styles.listItem}>E2 · 大型观察研究</Text>
            <Text style={styles.listItem}>E3 · 立场文件 / 机制综述</Text>
            <Text style={styles.listItem}>E4 · 专家公开观点</Text>
            <Text style={styles.caption}>所有建议都应保留证据层级与适用人群边界。</Text>
          </Section>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#F6F7F9' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12, padding: 24 },
  header: { paddingHorizontal: 20, paddingTop: 12, paddingBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  eyebrow: { fontSize: 11, letterSpacing: 1.8, color: '#667085', fontWeight: '700' },
  title: { fontSize: 30, fontWeight: '800', marginTop: 8, color: '#101828' },
  headerTitle: { fontSize: 22, fontWeight: '800', color: '#101828' },
  body: { fontSize: 15, lineHeight: 22, color: '#475467', marginTop: 8 },
  muted: { color: '#667085' },
  caption: { fontSize: 12, lineHeight: 18, color: '#98A2B3', marginTop: 12 },
  link: { color: '#344054', fontWeight: '700' },
  loginCard: { margin: 22, marginTop: 90, padding: 24, borderRadius: 24, backgroundColor: '#FFFFFF' },
  input: { marginTop: 24, borderWidth: 1, borderColor: '#D0D5DD', backgroundColor: '#FFFFFF', borderRadius: 14, paddingHorizontal: 14, paddingVertical: 13, fontSize: 16 },
  primaryButton: { marginTop: 14, backgroundColor: '#101828', borderRadius: 14, alignItems: 'center', paddingVertical: 14 },
  primaryButtonText: { color: '#FFFFFF', fontWeight: '800' },
  secondaryButton: { marginTop: 12, borderWidth: 1, borderColor: '#D0D5DD', borderRadius: 14, alignItems: 'center', paddingVertical: 13, backgroundColor: '#FFFFFF' },
  secondaryButtonText: { color: '#344054', fontWeight: '700' },
  tabBar: { flexDirection: 'row', marginHorizontal: 16, borderRadius: 14, padding: 4, backgroundColor: '#EAECF0' },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 9, borderRadius: 11 },
  tabActive: { backgroundColor: '#FFFFFF' },
  tabText: { fontSize: 13, color: '#667085', fontWeight: '600' },
  tabTextActive: { color: '#101828', fontWeight: '800' },
  scroll: { padding: 16, paddingBottom: 40 },
  heroCard: { borderRadius: 24, padding: 22, backgroundColor: '#FFFFFF' },
  heroLabel: { fontSize: 13, color: '#667085', fontWeight: '700' },
  heroScore: { marginTop: 8, fontSize: 52, fontWeight: '800', color: '#101828' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 12 },
  metricCard: { width: '48%', backgroundColor: '#FFFFFF', borderRadius: 18, padding: 16 },
  metricLabel: { fontSize: 12, color: '#667085' },
  metricValue: { marginTop: 8, fontSize: 20, fontWeight: '800', color: '#101828' },
  section: { marginTop: 12, backgroundColor: '#FFFFFF', borderRadius: 20, padding: 18 },
  sectionTitle: { fontSize: 17, fontWeight: '800', color: '#101828', marginBottom: 8 },
  listItem: { fontSize: 14, lineHeight: 22, color: '#475467', marginTop: 5 },
  warning: { color: '#B42318', marginTop: 10, fontSize: 13 },
});
