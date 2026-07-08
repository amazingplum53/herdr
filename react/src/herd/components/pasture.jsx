import { Link } from "react-router-dom";

export default function PastureList({
  farmId,
  pastures,
  onDeletePasture,
}) {
  if (pastures.length === 0) {
    return <p>No pastures yet.</p>;
  }

  return (
    <div>
      {pastures.map((pasture) => (
        <div key={pasture.id}>
          <h2>
            <Link
              to={`/farms/${farmId}/pastures/${pasture.id}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              {pasture.name}
            </Link>
          </h2>

          <button
            type="button"
            onClick={() => {
              if (window.confirm(`Delete pasture "${pasture.name}"?`)) {
                onDeletePasture(pasture.id);
              }
            }}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}