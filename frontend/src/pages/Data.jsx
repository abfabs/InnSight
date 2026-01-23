import "../styles/app.css";

export default function Data() {
  return (
    <div className="page">
      <section className="section" id="data">
        <div className="section-head">
          <h2 className="section-title">Data that tells a story</h2>
          <p className="section-subtitle">
            Not just charts—context you can act on.
          </p>
        </div>

        <div className="features">
          <div className="feature">
            <div className="feature-title">Sentiment</div>
            <div className="feature-text">
              Understand how guests feel, and what they talk about most.
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">Occupancy</div>
            <div className="feature-text">
              Compare demand patterns across neighborhoods and room types.
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">Top hosts</div>
            <div className="feature-text">
              Spot high-performing hosts and competitive clusters.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
