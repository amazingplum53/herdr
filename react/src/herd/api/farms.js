import { api } from "./api_handler";

export function getFarms() {
  return api("/api/farms/");
}

export function getFarm(farmId) {
  return api(`/api/farms/${farmId}/`);
}

export function createFarm(data) {
  return api("/api/farms/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateFarm(farmId, data) {
  return api(`/api/farms/${farmId}/`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteFarm(farmId) {
  return api(`/api/farms/${farmId}/`, {
    method: "DELETE",
  });
}