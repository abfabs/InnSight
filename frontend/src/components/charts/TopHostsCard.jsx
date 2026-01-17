import "../../styles/app.css";

function fmtRating(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(1);
}

export default function TopHostsCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;
  const hosts = Array.isArray(row?.top_hosts) ? row.top_hosts : [];

  return (
    <div className="cardbox">
      <div className="card-title-row">
        <h3>Top hosts</h3>
      </div>

      {hosts.length === 0 ? (
        <div className="muted" style={{ textAlign: "center", padding: "12px 0" }}>
          No data
        </div>
      ) : (
        <div className="list">
          {/* HEADER */}
          <div className="list-row list-header">
            <div className="host-left">
              <div className="host-rank">#</div>
              <div className="list-key">Host</div>
            </div>
            <div className="host-right">
              <div className="list-val">Listings</div>
              <div className="host-rating">Rating</div>
            </div>
          </div>

          {/* ROWS */}
          {hosts.slice(0, 10).map((h, i) => (
            <div key={h.host_id ?? `${h.host_name}-${i}`} className="list-row">
              <div className="host-left">
                <div className="host-rank">{i + 1}</div>
                <div className="list-key">{h.host_name}</div>
              </div>

              <div className="host-right">
                <div className="list-val">{Number(h.total_listings) || 0}</div>
                <div className="host-rating">{fmtRating(h.avg_rating)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
