import "../styles/app.css";

export default function About() {
  return (
    <div className="page">
      <section className="section">
        <div className="section-head">
          <h2 className="section-title">About InnSight</h2>
          <p className="section-subtitle">
            Your platform for Airbnb market intelligence and insights.
          </p>
        </div>

        <div className="features">
          <div className="feature">
            <div className="feature-title">Our Mission</div>
            <div className="feature-text">
              Empower hosts, travelers, and analysts with deep insights into short-term rental markets.
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">What We Do</div>
            <div className="feature-text">
              We analyze millions of listings and reviews to surface patterns that matter.
            </div>
          </div>

          <div className="feature">
            <div className="feature-title">Why Trust Us</div>
            <div className="feature-text">
              Built on real data, powered by NLP and geospatial analysis.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
