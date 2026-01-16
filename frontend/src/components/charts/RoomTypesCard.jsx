import "../../styles/app.css";

export default function RoomTypesCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;

  if (!row) {
    return <div className="cardbox"><h3>Room types</h3><div className="muted">No data</div></div>;
  }

  const entries = Object.entries(row.room_types || {});

  return (
    <div className="cardbox">
      <h3>Room types</h3>
      <div className="muted">Total listings: {row.total_listings}</div>
      <div className="list">
        {entries.map(([k, v]) => (
          <div key={k} className="list-row">
            <div className="list-key">{k}</div>
            <div className="list-val">{v.percentage}% ({v.count})</div>
          </div>
        ))}
      </div>
    </div>
  );
}
