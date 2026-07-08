import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { getPasture, updatePasture } from "../api/pastures";
import { getHerds } from "../api/herds";

export default function PastureManagementPage() {
  const { farmId, pastureId } = useParams();

  const [pasture, setPasture] = useState(null);
  const [herds, setHerds] = useState([]);
  const [selectedHerdId, setSelectedHerdId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadPasturePage() {
      setError("");

      const [pastureResponse, herdsResponse] = await Promise.all([
        getPasture(farmId, pastureId),
        getHerds(farmId),
      ]);

      if (!pastureResponse.ok || !herdsResponse.ok) {
        setError("Could not load pasture");
        return;
      }

      const pastureData = await pastureResponse.json();
      const herdsData = await herdsResponse.json();

      setPasture(pastureData);
      setHerds(herdsData);
    }

    loadPasturePage();
  }, [farmId, pastureId]);

  async function handleAddHerd(event) {
    event.preventDefault();
    setError("");

    const updatedHerdIds = [
      ...(pasture.herds || []),
      Number(selectedHerdId),
    ];

    const response = await updatePasture(farmId, pastureId, {
      herds: updatedHerdIds,
    });

    if (!response.ok) {
      setError("Could not add herd to pasture");
      return;
    }

    const updatedPasture = await response.json();

    setPasture(updatedPasture);
    setSelectedHerdId("");
  }

  async function handleRemoveHerd(herdId) {
    setError("");

    const updatedHerdIds = pasture.herds.filter((id) => id !== herdId);

    const response = await updatePasture(farmId, pastureId, {
      herds: updatedHerdIds,
    });

    if (!response.ok) {
      setError("Could not remove herd from pasture");
      return;
    }

    const updatedPasture = await response.json();

    setPasture(updatedPasture);
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (!pasture) {
    return <p>Loading...</p>;
  }

  const assignedHerds = herds.filter((herd) =>
    pasture.herds?.includes(herd.id)
  );

  const availableHerds = herds.filter(
    (herd) => !pasture.herds?.includes(herd.id)
  );

  return (
    <div>
      <Link to={`/farms/${farmId}`}>
        <h3>Back</h3>
      </Link>

      <h1>{pasture.name}</h1>

      <section>
        <h2>Herds in this pasture</h2>

        {assignedHerds.length ? (
          <ul>
            {assignedHerds.map((herd) => (
              <li key={herd.id}>
                {herd.name}{" "}
                <button
                  type="button"
                  onClick={() => handleRemoveHerd(herd.id)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p>No herds assigned to this pasture.</p>
        )}
      </section>

      <section>
        <h2>Add herd</h2>

        {availableHerds.length ? (
          <form onSubmit={handleAddHerd}>
            <select
              value={selectedHerdId}
              onChange={(event) => setSelectedHerdId(event.target.value)}
              required
            >
              <option value="">Select a herd</option>

              {availableHerds.map((herd) => (
                <option key={herd.id} value={herd.id}>
                  {herd.name}
                </option>
              ))}
            </select>

            <button type="submit">Add herd</button>
          </form>
        ) : (
          <p>All herds are already assigned to this pasture.</p>
        )}
      </section>
    </div>
  );
}