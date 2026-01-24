import "../styles/app.css";

export default function About() {
  return (
    <div className="page about-page">
      {/* HERO */}
      <section className="section about-hero">
        <div className="about-hero__inner">
          <p className="about-badge">ABOUT</p>
          <h1 className="about-title">About InnSight</h1>
          <p className="about-subtitle">
            InnSight is a market intelligence platform for short-term rentals. We
            combine structured listing data, review text, and availability signals to
            reveal how neighborhoods perform—so decisions are based on evidence, not guesswork.
          </p>

          <div className="about-metrics">
            <div className="about-metric">
              <div className="about-metric__value">City-first</div>
              <div className="about-metric__label">Comparable views across locations</div>
            </div>
            <div className="about-metric">
              <div className="about-metric__value">Neighborhood-level</div>
              <div className="about-metric__label">Insights where decisions happen</div>
            </div>
            <div className="about-metric">
              <div className="about-metric__value">Data + NLP</div>
              <div className="about-metric__label">Signals with context, not noise</div>
            </div>
          </div>
        </div>
      </section>

      {/* CORE */}
      <section className="section">
        <div className="section-head">
          <h2 className="section-title">What we stand for</h2>
          <p className="section-subtitle">
            The goal isn’t to overwhelm users with dashboards. It’s to make the market legible.
          </p>
        </div>

        <div className="about-grid">
          <div className="about-card">
            <div className="about-card__title">Our mission</div>
            <div className="about-card__text">
              Empower hosts, travelers, and analysts with clear insights into
              short-term rental markets—so pricing, positioning, and neighborhood
              choices are informed and defensible.
            </div>
          </div>

          <div className="about-card">
            <div className="about-card__title">What we do</div>
            <div className="about-card__text">
              We transform raw datasets into neighborhood summaries: sentiment,
              demand/availability signals, room-type differences, and competitive host patterns.
            </div>
          </div>

          <div className="about-card">
            <div className="about-card__title">Why it matters</div>
            <div className="about-card__text">
              A city can look strong on average while certain neighborhoods underperform.
              InnSight helps you zoom in and understand what’s driving outcomes.
            </div>
          </div>

          <div className="about-card">
            <div className="about-card__title">Trust & transparency</div>
            <div className="about-card__text">
              Our insights are built from real datasets and consistent processing rules.
              We focus on explainable signals—pairing metrics with the “why” behind them.
            </div>
          </div>
        </div>
      </section>

      {/* WHO IT HELPS */}
      <section className="section about-split">
        <div className="about-split__left">
          <h2 className="about-split__title">Who it’s for</h2>
          <p className="about-split__text">
            InnSight supports different use cases without changing the mental model:
            select a city, choose a neighborhood, compare signals, and act.
          </p>

          <div className="about-list">
            <div className="about-list__item">
              <div className="about-list__title">Hosts</div>
              <div className="about-list__text">
                Benchmark your area, identify what guests care about, and spot competitive clusters.
              </div>
            </div>

            <div className="about-list__item">
              <div className="about-list__title">Travelers</div>
              <div className="about-list__text">
                Understand neighborhood “vibes” using real review language and sentiment breakdowns.
              </div>
            </div>

            <div className="about-list__item">
              <div className="about-list__title">Analysts & researchers</div>
              <div className="about-list__text">
                Explore consistent, comparable metrics across cities for market-level insights.
              </div>
            </div>
          </div>
        </div>

        <div className="about-split__right">
          <div className="about-callout">
            <div className="about-callout__title">What you can discover</div>
            <ul className="about-callout__list">
              <li>Which neighborhoods are most positively reviewed, and why.</li>
              <li>Where complaints cluster (noise, cleanliness, check-in, location).</li>
              <li>Room-type differences by neighborhood (entire home vs private room).</li>
              <li>Availability patterns that suggest demand shifts or seasonality.</li>
              <li>Host concentration and competition intensity.</li>
            </ul>
          </div>

          <div className="about-note">
            <div className="about-note__title">A note on limitations</div>
            <div className="about-note__text">
              Reviews reflect who chooses to write them, and availability is a proxy—not a
              confirmed booking record. InnSight is designed for directional intelligence
              and transparent comparison.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
