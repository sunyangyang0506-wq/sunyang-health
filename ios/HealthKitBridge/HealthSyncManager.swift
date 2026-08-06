import Foundation
import HealthKit

/// Prototype HealthKit bridge.
/// The app must request user authorization before reading health data.
/// Exported records are sent to the backend /v1/sync/apple-health endpoint.

final class HealthSyncManager {
    private let store = HKHealthStore()

    private let readTypes: Set<HKObjectType> = [
        HKObjectType.quantityType(forIdentifier: .stepCount)!,
        HKObjectType.quantityType(forIdentifier: .bodyMass)!,
        HKObjectType.quantityType(forIdentifier: .heartRate)!,
        HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
        HKObjectType.quantityType(forIdentifier: .vo2Max)!
    ]

    func requestAuthorization(completion: @escaping (Bool) -> Void) {
        store.requestAuthorization(toShare: [], read: readTypes) { success, _ in
            completion(success)
        }
    }

    func syncRecords(to endpoint: URL, token: String) {
        // Implementation placeholder:
        // 1. Query HKSampleQuery
        // 2. Convert HealthKit samples to neutral JSON contract
        // 3. POST with Authorization: Bearer <token>
    }
}
