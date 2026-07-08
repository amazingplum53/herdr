import { api } from "./api_handler";

export function getPastures(farmId) {
  return api(`/api/farms/${farmId}/pastures/`);
}

export function getPasture(farmId, pastureId) {
  return api(`/api/farms/${farmId}/pastures/${pastureId}/`);
}

export function createPasture(farmId, data) {
  return api(`/api/farms/${farmId}/pastures/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updatePasture(farmId, pastureId, data) {
  return api(`/api/farms/${farmId}/pastures/${pastureId}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deletePasture(farmId, pastureId) {
  return api(`/api/farms/${farmId}/pastures/${pastureId}/`, {
    method: "DELETE",
  });
}

