import type { HealthRecord } from './api';

export async function connectHealthData(): Promise<string> {
  return '当前平台尚未启用原生健康数据连接。';
}

export async function collectHealthRecords(): Promise<HealthRecord[]> {
  return [];
}
