# iOS HealthKit Integration

## Flow

```text
Apple Watch
    |
    v
HealthKit
    |
    v
HealthSyncManager
    |
    v
POST /v1/sync/apple-health
    |
    v
Personal Health Digital Twin
```

## Authorization

The iOS app must request HealthKit permissions from the user.

The backend never bypasses Apple Health privacy controls.

## Data Contract

The bridge sends normalized records:

```json
{
  "type":"HKQuantityTypeIdentifierStepCount",
  "value":8000,
  "unit":"count",
  "start_date":"2026-08-07T06:30:00+08:00",
  "source":"Apple Watch"
}
```

## Production Next Steps

- complete HKSampleQuery implementations
- add background delivery observer
- add secure token/key management
- add user consent management
