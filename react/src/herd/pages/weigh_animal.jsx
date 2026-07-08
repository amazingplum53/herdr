import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

import { searchAnimals } from "../api/animals";
import { createMeasurement, getMeasurements } from "../api/measurements";

export default function WeighAnimalPage() {
  const { farmId } = useParams();

  const [search, setSearch] = useState("");
  const [animals, setAnimals] = useState([]);
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [weight, setWeight] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadMeasurements(animalId) {
    const response = await getMeasurements(farmId, animalId);

    if (!response.ok) {
      throw new Error("Could not load measurements.");
    }

    const data = await response.json();

    setMeasurements(
      data.map((measurement) => ({
        ...measurement,
        weight: Number(measurement.weight),
        date: new Date(measurement.measured_at).toLocaleDateString(),
      }))
    );
  }

  async function handleSearch(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSelectedAnimal(null);
    setMeasurements([]);

    try {
      const response = await searchAnimals(farmId, search);

      if (!response.ok) {
        throw new Error("Could not search animals.");
      }

      const results = await response.json();
      setAnimals(results);
    } catch {
      setError("Could not search animals.");
    }
  }

  async function handleSelectAnimal(animal) {
    setSelectedAnimal(animal);
    setSuccess("");
    setError("");

    try {
      await loadMeasurements(animal.id);
    } catch {
      setError("Could not load measurements.");
    }
  }

  async function handleSaveMeasurement(event) {
    event.preventDefault();

    if (!selectedAnimal) {
      setError("Select an animal first.");
      return;
    }

    if (!weight) {
      setError("Enter a weight.");
      return;
    }

    setError("");
    setSuccess("");

    try {
      const response = await createMeasurement(farmId, selectedAnimal.id, {
        weight,
        measured_at: new Date().toISOString(),
      });

      if (!response.ok) {
        throw new Error("Could not save measurement.");
      }

      setSuccess(`Saved ${weight} kg for ${selectedAnimal.animal_id}.`);
      setWeight("");

      await loadMeasurements(selectedAnimal.id);
    } catch {
      setError("Could not save measurement.");
    }
  }

  return (
    <main>
      <p>
        <Link to={`/farms/${farmId}`}>Back to Farm</Link>
      </p>

      <h1>Weigh Animal</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {success && <p style={{ color: "green" }}>{success}</p>}

      <form onSubmit={handleSearch}>
        <label>
          Animal ID
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search animal ID"
          />
        </label>

        <button type="submit">Search</button>
      </form>

      <h2>Matching animals</h2>

      {animals.length === 0 ? (
        <p>No animals found.</p>
      ) : (
        <ul>
          {animals.map((animal) => (
            <li key={animal.id}>
              <button type="button" onClick={() => handleSelectAnimal(animal)}>
                {animal.animal_id} — {animal.species} — Latest weight:{" "}
                {animal.latest_weight ?? "None"} kg
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedAnimal && (
        <section>
          <h2>Selected animal</h2>

          <p>
            <strong>ID:</strong> {selectedAnimal.animal_id}
          </p>

          <p>
            <strong>Species:</strong> {selectedAnimal.species}
          </p>

          <p>
            <strong>Latest weight:</strong>{" "}
            {selectedAnimal.latest_weight ?? "None"} kg
          </p>

          <form onSubmit={handleSaveMeasurement}>
            <label>
              New weight kg
              <input
                type="number"
                step="0.01"
                value={weight}
                onChange={(event) => setWeight(event.target.value)}
              />
            </label>

            <button type="submit">Save measurement</button>
          </form>

          <h2>Weight history</h2>

          {measurements.length === 0 ? (
            <p>No measurements yet.</p>
          ) : (
            <div style={{ width: "100%", height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={measurements}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="weight" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
      )}
    </main>
  );
}