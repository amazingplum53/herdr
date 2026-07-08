import { Link } from "react-router-dom";

export default function HerdList({ farmId, herds, onDeleteHerd }) {
  if (herds.length === 0) {
    return <p>No herds yet.</p>;
  }

  return (
    <div>
      {herds.map((herd) => (
        <Link
          key={herd.id}
          to={`/farms/${farmId}/herds/${herd.id}`}
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <div>
            <h3>{herd.name}</h3>
            <p>Animals: {herd.animal_count}</p>

            <button
              type="button"
              onClick={(event) => {
                event.preventDefault();
                event.stopPropagation();

                if (window.confirm(`Delete herd "${herd.name}"?`)) {
                  onDeleteHerd(herd.id);
                }
              }}
            >
              Delete
            </button>
          </div>
        </Link>
      ))}
    </div>
  );
}