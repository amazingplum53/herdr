import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getFarms, createFarm } from "../api/farms";
import LogoutButton from "../../user/logout_button";

import FarmDisplay from "../components/farm";

export default function DashboardPage() {
  const [farms, setFarms] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function loadFarms() {
    const response = await getFarms();

    if (!response.ok) {
      setError("Could not load farms");
      return;
    }

    const data = await response.json();
    setFarms(data);
  }

  useEffect(() => {
    loadFarms();
  }, []);

  async function handleCreateFarm(event) {
    event.preventDefault();
    setError("");

    const response = await createFarm({
      name,
      address_line_1: "Test address",
      postcode: "TEST",
      country: "UK",
    });

    if (!response.ok) {
      const data = await response.json();
      setError(JSON.stringify(data));
      return;
    }

    setName("");
    await loadFarms();
  }

  return (
    <div>
      <h1>Dashboard</h1>

      <LogoutButton />

      {error && <p>{error}</p>}

      <h2>Create farm</h2>

      <form onSubmit={handleCreateFarm}>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Farm name"
        />

        <button type="submit">Create farm</button>
      </form>

      <h2>Farms</h2>

      {farms.map((farm) => (
        <Link
          key={farm.id}
          to={`/farms/${farm.id}`}
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <FarmDisplay farm={farm} />  
        </Link>
      ))}
    </div>
  );
}