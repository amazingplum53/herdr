import { useEffect, useState } from "react";
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

import LogoutButton from "../../user/logout_button";
import { getHerd } from "../api/herds";
import { createAnimal } from "../api/animals";
import { getHerdPerformance } from "../api/measurements";

const ANIMALS_PER_PAGE = 10;

export default function HerdManagmentPage() {
  const { farmId, herdId } = useParams();

  const [animalId, setAnimalId] = useState("");
  const [species, setSpecies] = useState("");
  const [animals, setAnimals] = useState([]);
  const [page, setPage] = useState(1);
  const [performance, setPerformance] = useState([]);
  const [error, setError] = useState("");

  async function handleAddAnimal(event) {
    event.preventDefault();
    setError("");

    try {
      const response = await createAnimal(farmId, {
        herd: herdId,
        animal_id: animalId,
        species,
      });

      const newAnimal = await response.json();

      setAnimals((currentAnimals) => [...currentAnimals, newAnimal]);
      setAnimalId("");
      setSpecies("");
    } catch {
      setError("Could not add animal.");
    }
  }

  useEffect(() => {
  async function loadHerd() {
    setError("");

    try {
      const herdResponse = await getHerd(farmId, herdId);

      if (!herdResponse.ok) {
        setError("Could not load herd.");
        return;
      }

      const herd = await herdResponse.json();
      setAnimals(herd.animals || []);

      const performanceResponse = await getHerdPerformance(farmId, herdId);

      if (!performanceResponse.ok) {
        setError("Could not load herd performance.");
        return;
      }

      const performanceData = await performanceResponse.json();

      setPerformance(
        performanceData.map((point) => ({
          date: point.date,
          average_weight: Number(point.average_weight),
        }))
      );
    } catch {
      setError("Could not load herd.");
    }
  }

  loadHerd();
  }, [farmId, herdId]);

  const totalPages = Math.ceil(animals.length / ANIMALS_PER_PAGE);

  const visibleAnimals = animals.slice(
    (page - 1) * ANIMALS_PER_PAGE,
    page * ANIMALS_PER_PAGE
  );

  return (
    <main>
      <LogoutButton />

      <p>
        <Link to={`/farms/${farmId}`}>Back to Farm</Link>
      </p>

      <h1>Herd</h1>

      {error && <p>{error}</p>}

      <h2>Animals</h2>

      <form onSubmit={handleAddAnimal}>
        <label>
          Animal ID
          <input
            value={animalId}
            onChange={(event) => setAnimalId(event.target.value)}
            required
          />
        </label>

        <label>
          Species
          <select
            value={species}
            onChange={(event) => setSpecies(event.target.value)}
            required
          >
            <option value="">Select species</option>
            <option value="sheep">Sheep</option>
            <option value="cattle">Cattle</option>
            <option value="pig">Pig</option>
          </select>
        </label>

        <button type="submit">Add animal</button>
      </form>

      <p>{animals.length} animals</p>

      {visibleAnimals.length === 0 ? (
        <p>No animals in this herd yet.</p>
      ) : (
        <ul>
          {visibleAnimals.map((animal) => (
            <li key={animal.id}>
              {animal.animal_id} - {animal.species}
            </li>
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <div>
          <button
            disabled={page === 1}
            onClick={() => setPage((currentPage) => currentPage - 1)}
          >
            Previous
          </button>

          <span> Page {page} of {totalPages} </span>

          <button
            disabled={page === totalPages}
            onClick={() => setPage((currentPage) => currentPage + 1)}
          >
            Next
          </button>
        </div>
      )}

      <h2>Herd weight history</h2>

      {performance.length === 0 ? (
        <p>No measurements yet.</p>
      ) : (
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="average_weight"
                name="Average Weight (kg)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </main>
  );
}