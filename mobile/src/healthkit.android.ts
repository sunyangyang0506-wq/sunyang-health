import type { HealthRecord } from './api';

export async function connectHealthData(): Promise<string> {
  return 'Android 版本下一步接入 Health Connect；当前健康数据直连优先完成 iOS HealthKit。';
}

export async function collectHealthRecords(): Promise<HealthRecord[]> {
  return [];
}
