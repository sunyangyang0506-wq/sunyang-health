export type HealthSummary = {
  record_date?: string;
  readiness?: {
    level?: string;
    score?: number;
    summary?: string;
    reasons?: string[];
  };
  metrics?: {
    sleep_hours?: number | null;
    hrv_ms?: number | null;
    resting_heart_rate?: number | null;
    steps?: number | null;
    weight_kg?: number | null;
    body_fat_percent?: number | null;
    lean_mass_kg?: number | null;
  };
  actions?: string[];
  data_quality?: Record<string, unknown>;
};

const apiBase = (process.env.EXPO_PUBLIC_API_BASE || '').replace(/\/$/, '');

function requireApiBase(): string {
  if (!apiBase) {
    throw new Error('EXPO_PUBLIC_API_BASE is not configured');
  }
  return apiBase;
}

export async function enroll(enrollmentCode: string): Promise<string> {
  const response = await fetch(`${requireApiBase()}/v1/app/enroll`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enrollment_code: enrollmentCode.trim() }),
  });
  if (!response.ok) {
    throw new Error(response.status === 401 ? '配对码无效' : `登录失败 (${response.status})`);
  }
  const data = await response.json();
  if (!data.session_token) throw new Error('服务端未返回会话令牌');
  return data.session_token as string;
}

export async function getSummary(sessionToken: string): Promise<HealthSummary> {
  const response = await fetch(`${requireApiBase()}/v1/app/summary`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  if (!response.ok) {
    const error = new Error(response.status === 401 ? 'SESSION_EXPIRED' : `数据加载失败 (${response.status})`);
    throw error;
  }
  return response.json();
}
