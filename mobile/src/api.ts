export type HealthRecord = {
  metric: string;
  value: number;
  unit?: string;
  recorded_at: string;
  record_date?: string;
  source?: string;
  confidence?: string;
};

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

export type SyncResult = {
  normalized_records?: number;
  written_records?: number;
  days?: number;
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

export async function syncAppleHealth(
  sessionToken: string,
  records: HealthRecord[]
): Promise<SyncResult> {
  const response = await fetch(`${requireApiBase()}/v1/app/sync/apple-health`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${sessionToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ records }),
  });
  if (!response.ok) {
    if (response.status === 401) throw new Error('SESSION_EXPIRED');
    throw new Error(`健康数据同步失败 (${response.status})`);
  }
  return response.json();
}

export async function getSummary(
  sessionToken: string,
  localDate?: string
): Promise<HealthSummary> {
  const query = localDate ? `?record_date=${encodeURIComponent(localDate)}` : '';
  const response = await fetch(`${requireApiBase()}/v1/app/summary${query}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  if (!response.ok) {
    const error = new Error(response.status === 401 ? 'SESSION_EXPIRED' : `数据加载失败 (${response.status})`);
    throw error;
  }
  return response.json();
}
