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