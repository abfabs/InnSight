import "../styles/app.css";

export default function Technology() {
  return (
    <div className="page">
      <section className="section" id="technology">
        <div className="section-head">
          <h2 className="section-title">How it works</h2>
          <p className="section-subtitle">
            From raw listings to clean insights—end to end.
          </p>
        </div>

        <div className="steps">
          <div className="step">
            <div className="step-num">01</div>
            <div className="step-title">Ingest</div>
            <div className="step-text">
              Load listing & review datasets, normalize and clean.
            </div>
          </div>

          <div className="step">
            <div className="step-num">02</div>
            <div className="step-title">Analyze</div>
            <div className="step-text">
              NLP sentiment aggregation by city and neighborhood.
            </div>
          </div>

          <div className="step">
            <div className="step-num">03</div>
            <div className="step-title">Explore</div>
            <div className="step-text">
              Interactive map + dashboard cards for fast comparisons.
            </div>
          </div>
        </div>

        <div className="section-head" style={{ marginTop: "40px" }}>
          <h3 className="section-title">Tech Stack</h3>
        </div>

        <div className="features">
          <div className="feature">
            <div className="feature-title">Backend</div>
            <div className="feature-text">
              Python, Flask, MongoDB for data storage and REST API
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">Frontend</div>
            <div className="feature-text">
              React, Vite, Leaflet/Maplibre for interactive mapping
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">Analytics</div>
            <div className="feature-text">
              spaCy NLP, sentiment analysis, aggregation pipelines
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
