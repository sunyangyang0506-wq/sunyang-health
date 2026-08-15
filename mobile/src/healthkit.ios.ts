import {
  getMostRecentQuantitySample,
  isHealthDataAvailable,
  queryCategorySamples,
  queryQuantitySamples,
  requestAuthorization,
} from '@kingstinct/react-native-healthkit';

import type { HealthRecord } from './api';

const readTypes = [
  'HKQuantityTypeIdentifierStepCount',
  'HKQuantityTypeIdentifierActiveEnergyBurned',
  'HKQuantityTypeIdentifierAppleExerciseTime',
  'HKQuantityTypeIdentifierDistanceWalkingRunning',
  'HKQuantityTypeIdentifierRestingHeartRate',
  'HKQuantityTypeIdentifierHeartRateVariabilitySDNN',
  'HKQuantityTypeIdentifierBodyMass',
  'HKQuantityTypeIdentifierBodyFatPercentage',
  'HKQuantityTypeIdentifierLeanBodyMass',
  'HKCategoryTypeIdentifierSleepAnalysis',
] as const;

const quantityMetricMap: Record<string, string> = {
  HKQuantityTypeIdentifierRestingHeartRate: 'restingHeartRate',
  HKQuantityTypeIdentifierHeartRateVariabilitySDNN: 'heartRateVariabilitySDNN',
  HKQuantityTypeIdentifierBodyMass: 'bodyMass',
  HKQuantityTypeIdentifierBodyFatPercentage: 'bodyFatPercentage',
  HKQuantityTypeIdentifierLeanBodyMass: 'leanBodyMass',
};

const cumulativeMetricMap: Record<string, string> = {
  HKQuantityTypeIdentifierStepCount: 'stepCount',
  HKQuantityTypeIdentifierActiveEnergyBurned: 'activeEnergyBurned',
  HKQuantityTypeIdentifierAppleExerciseTime: 'appleExerciseTime',
  HKQuantityTypeIdentifierDistanceWalkingRunning: 'distanceWalkingRunning',
};

function unwrapSamples(result: any): any[] {
  if (Array.isArray(result)) return result;
  return Array.isArray(result?.samples) ? result.samples : [];
}

function localDateKey(value: string | Date): string {
  const date = value instanceof Date ? value : new Date(value);
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function sampleDate(sample: any): string {
  return sample?.endDate || sample?.startDate || new Date().toISOString();
}

function quantityValue(sample: any): number | null {
  const value = Number(sample?.quantity ?? sample?.value);
  return Number.isFinite(value) ? value : null;
}

function isAsleepValue(value: unknown): boolean {
  if (typeof value === 'number') {
    return value === 1 || value === 3 || value === 4 || value === 5;
  }
  const text = String(value ?? '').toLowerCase();
  return text.includes('asleep') || text.includes('core') || text.includes('deep') || text.includes('rem');
}

function durationHours(startDate: string, endDate: string): number {
  const ms = new Date(endDate).getTime() - new Date(startDate).getTime();
  return Math.max(0, ms / 3_600_000);
}

async function authorize(): Promise<void> {
  const available = await isHealthDataAvailable();
  if (!available) throw new Error('当前设备不可用 HealthKit');
  await requestAuthorization({ toRead: [...readTypes] });
}

export async function connectHealthData(): Promise<string> {
  await authorize();
  return 'HealthKit 授权流程已完成；读取范围由系统授权决定';
}

export async function collectHealthRecords(): Promise<HealthRecord[]> {
  await authorize();

  const now = new Date();
  const todayKey = localDateKey(now);
  const records: HealthRecord[] = [];

  for (const [identifier, metric] of Object.entries(quantityMetricMap)) {
    try {
      const sample: any = await getMostRecentQuantitySample(identifier as any);
      const value = quantityValue(sample);
      if (value === null) continue;
      const recordedAt = sampleDate(sample);
      records.push({
        metric,
        value,
        unit: sample?.unit,
        recorded_at: recordedAt,
        record_date: localDateKey(recordedAt),
        source: 'Apple Health',
        confidence: 'B',
      });
    } catch {
      // A denied or missing HealthKit type must not abort the remaining sync.
    }
  }

  for (const [identifier, metric] of Object.entries(cumulativeMetricMap)) {
    try {
      const result: any = await queryQuantitySamples(identifier as any, { limit: 2000 } as any);
      const samples = unwrapSamples(result).filter((sample) => localDateKey(sampleDate(sample)) === todayKey);
      const value = samples.reduce((sum, sample) => sum + (quantityValue(sample) ?? 0), 0);
      if (!samples.length || !Number.isFinite(value)) continue;
      const last = samples[samples.length - 1];
      records.push({
        metric,
        value,
        unit: last?.unit,
        recorded_at: now.toISOString(),
        record_date: todayKey,
        source: 'Apple Health',
        confidence: 'B',
      });
    } catch {
      // Keep partial sync usable when one cumulative metric is unavailable.
    }
  }

  try {
    const result: any = await queryCategorySamples('HKCategoryTypeIdentifierSleepAnalysis' as any, {
      limit: 100,
    } as any);
    const cutoff = now.getTime() - 18 * 60 * 60 * 1000;
    const sleepSamples = unwrapSamples(result).filter((sample) => {
      const end = new Date(sampleDate(sample)).getTime();
      return end >= cutoff && isAsleepValue(sample?.value);
    });
    const hours = sleepSamples.reduce(
      (sum, sample) => sum + durationHours(sample.startDate, sample.endDate),
      0
    );
    if (hours > 0) {
      records.push({
        metric: 'sleepAnalysis',
        value: Math.round(hours * 100) / 100,
        unit: 'h',
        recorded_at: now.toISOString(),
        record_date: todayKey,
        source: 'Apple Health',
        confidence: 'B',
      });
    }
  } catch {
    // Sleep permission/data may be absent; the app will display data quality accordingly.
  }

  return records;
}
