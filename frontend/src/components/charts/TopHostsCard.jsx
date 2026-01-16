import "../../styles/app.css";

export default function TopHostsCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;
  const hosts = row?.top_hosts || [];

  if (!row) {
    return <div className="cardbox"><h3>Top hosts</h3><div className="muted">No data</div></div>;
  }

  return (
    <div className="cardbox">
      <h3>Top hosts</h3>
      <div className="list">
        {hosts.map((h) => (
          <div key={h.host_id} className="list-row">
            <div className="list-key">{h.host_name}</div>
            <div className="list-val">{h.total_listings} listings</div>
          </div>
        ))}
      </div>
    </div>
  );
}
