import { api } from "./api_handler";

export function getAnimals(farmId) {
  return api(`/api/farms/${farmId}/animals/`);
}

export function getAnimal(farmId, animalId) {
  return api(`/api/farms/${farmId}/animals/${animalId}/`);
}

export function searchAnimals(farmId, search) {
  return api(
    `/api/farms/${farmId}/animals/?search=${encodeURIComponent(search)}`
  );
}

export function createAnimal(farmId, data) {
  return api(`/api/farms/${farmId}/animals/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateAnimal(farmId, animalId, data) {
  return api(`/api/farms/${farmId}/animals/${animalId}/`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteAnimal(farmId, animalId) {
  return api(`/api/farms/${farmId}/animals/${animalId}/`, {
    method: "DELETE",
  });
}