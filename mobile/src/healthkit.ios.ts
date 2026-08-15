import { isHealthDataAvailable, requestAuthorization } from '@kingstinct/react-native-healthkit';

const readTypes = [
  'HKQuantityTypeIdentifierStepCount',
  'HKQuantityTypeIdentifierHeartRate',
  'HKQuantityTypeIdentifierRestingHeartRate',
  'HKQuantityTypeIdentifierHeartRateVariabilitySDNN',
  'HKQuantityTypeIdentifierBodyMass',
  'HKQuantityTypeIdentifierBodyFatPercentage',
  'HKCategoryTypeIdentifierSleepAnalysis',
] as const;

export async function connectHealthData(): Promise<string> {
  const available = await isHealthDataAvailable();
  if (!available) return '当前设备不可用 HealthKit';

  await requestAuthorization({ toRead: [...readTypes] });
  return 'HealthKit 授权流程已完成；后续读取权限以系统授权结果为准';
}
