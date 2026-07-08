import { api } from "./api_handler";

export function getHerds(farmId) {
  return api(`/api/farms/${farmId}/herds/`);
}

export function getHerd(farmId, herdId) {
  return api(`/api/farms/${farmId}/herds/${herdId}/`);
}

export function createHerd(farmId, data) {
  return api(`/api/farms/${farmId}/herds/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateHerd(farmId, herdId, data) {
  return api(`/api/farms/${farmId}/herds/${herdId}/`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteHerd(farmId, herdId) {
  return api(`/api/farms/${farmId}/herds/${herdId}/`, {
    method: "DELETE",
  });
}