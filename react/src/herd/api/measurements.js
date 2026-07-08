import { api } from "./api_handler";

export function createMeasurement(farmId, animalId, data) {
  return api(
    `/api/farms/${farmId}/animals/${animalId}/measurements/`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

export function getMeasurements(farmId, animalId) {
  return api(`/api/farms/${farmId}/animals/${animalId}/measurements/`);
}

export function getHerdPerformance(farmId, herdId) {
  return api(`/api/farms/${farmId}/herds/${herdId}/performance/`);
}