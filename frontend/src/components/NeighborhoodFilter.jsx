import "../styles/app.css";

export default function NeighborhoodFilter({ neighborhoods, value, onChange }) {
  return (
    <div className="filter" onSubmit={(e) => e.preventDefault()}>
      <label className="filter-label">Neighborhood</label>
      <select
        className="filter-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {neighborhoods.map((n) => (
          <option key={n} value={n}>
            {n}
          </option>
        ))}
      </select>
    </div>
  );
}
