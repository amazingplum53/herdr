import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import LogoutButton from "../../user/logout_button";

import { getFarm } from "../api/farms";
import { getHerds, createHerd, deleteHerd } from "../api/herds";
import { getPastures, createPasture, deletePasture } from "../api/pastures";

import FarmDisplay from "../components/farm";
import HerdList from "../components/herd";
import PastureList from "../components/pasture";

export default function FarmOverviewPage() {
  const { farmId } = useParams();

  const [farm, setFarm] = useState(null);
  const [herds, setHerds] = useState([]);
  const [herdName, setHerdName] = useState("");
  const [pastureName, setPastureName] = useState("");
  const [pastures, setPastures] = useState([]);
  const [error, setError] = useState("");

  async function handleCreateHerd(event) {
    event.preventDefault();
    setError("");

    const response = await createHerd(farmId, {
      farm: farmId,
      name: herdName,
    });

    if (!response.ok) {
      setError("Could not create herd");
      return;
    }

    const newHerd = await response.json();

    setHerds((currentHerds) => [...currentHerds, newHerd]);
    setHerdName("");
  }

  async function handleDeleteHerd(herdId) {
    setError("");

    const response = await deleteHerd(farmId, herdId);

    if (!response.ok) {
      setError("Could not delete herd");
      return;
    }

    setHerds((currentHerds) =>
      currentHerds.filter((herd) => herd.id !== herdId)
    );
  }

  async function handleCreatePasture(event) {
    event.preventDefault();
    setError("");

    const response = await createPasture(farmId, {
      farm: farmId,
      name: pastureName,
    });

    if (!response.ok) {
      setError("Could not create pasture");
      return;
    }

    const newPasture = await response.json();

    setPastures((currentPastures) => [...currentPastures, newPasture]);
    setPastureName("");
  }

  async function handleDeletePasture(pastureId) {
    setError("");

    const response = await deletePasture(farmId, pastureId);

    if (!response.ok) {
      setError("Could not delete pasture");
      return;
    }

    setPastures((currentPastures) =>
      currentPastures.filter((pasture) => pasture.id !== pastureId)
    );
  }

  useEffect(() => {
    async function loadFarmOverview() {
      setError("");

      const [farmResponse, herdsResponse, pasturesResponse] =
        await Promise.all([
          getFarm(farmId),
          getHerds(farmId),
          getPastures(farmId),
        ]);

      if (!farmResponse.ok || !herdsResponse.ok || !pasturesResponse.ok) {
        setError("Could not load farm overview");
        return;
      }

      const farmData = await farmResponse.json();
      const herdsData = await herdsResponse.json();
      const pasturesData = await pasturesResponse.json();

      setFarm(farmData);
      setHerds(herdsData);
      setPastures(pasturesData);
    }

    loadFarmOverview();
  }, [farmId]);

  if (error) {
    return <p>{error}</p>;
  }

  if (!farm) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <p>
        <Link to={`/`}>Back</Link>
      </p>

      <LogoutButton />

      <FarmDisplay farm={farm} />

      <section>
        <Link to={`/farms/${farmId}/new-measurement/`}>
          <h2>Weigh Animal</h2>
        </Link>
      </section>

      <section>
        <h2>Herds</h2>

        <form onSubmit={handleCreateHerd}>
          <label>
            Herd name
            <input
              value={herdName}
              onChange={(event) => setHerdName(event.target.value)}
              required
            />
          </label>

          <button type="submit">Add herd</button>
        </form>

        <HerdList
          farmId={farmId}
          herds={herds}
          onDeleteHerd={handleDeleteHerd}
        />
      </section>

      <section>
        <h2>Pastures</h2>

        <form onSubmit={handleCreatePasture}>
          <label>
            Pasture name
            <input
              value={pastureName}
              onChange={(event) => setPastureName(event.target.value)}
              required
            />
          </label>

          <button type="submit">Add pasture</button>
        </form>

        <PastureList
          farmId={farmId}
          pastures={pastures}
          onDeletePasture={handleDeletePasture}
        />
      </section>
    </div>
  );
}