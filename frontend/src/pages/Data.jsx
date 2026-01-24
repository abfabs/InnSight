import "../styles/app.css";

export default function Data() {
  return (
    <div className="page data-page">
      {/* HERO */}
      <section className="section data-hero">
        <div className="data-hero__inner">
          <p className="data-badge">DATA & PIPELINE</p>
          <h1 className="data-title">How InnSight uses data</h1>
          <p className="data-subtitle">
            We turn listings, reviews, and availability into neighborhood insights:
            sentiment, demand signals, and competitive context—across every city.
          </p>

          <div className="data-pipeline">
            <div className="pipe-step">
              <div className="pipe-dot" />
              <div>
                <div className="pipe-title">Collect</div>
                <div className="pipe-text">Listings • Reviews • Calendar</div>
              </div>
            </div>

            <div className="pipe-step">
              <div className="pipe-dot" />
              <div>
                <div className="pipe-title">Clean</div>
                <div className="pipe-text">Normalize • Deduplicate • Validate</div>
              </div>
            </div>

            <div className="pipe-step">
              <div className="pipe-dot" />
              <div>
                <div className="pipe-title">Enrich</div>
                <div className="pipe-text">Sentiment • Keywords • Aggregates</div>
              </div>
            </div>

            <div className="pipe-step">
              <div className="pipe-dot" />
              <div>
                <div className="pipe-title">Serve</div>
                <div className="pipe-text">Fast API • Dashboard</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* WHAT YOU GET */}
      <section className="section">
        <div className="section-head data-head">
          <h2 className="section-title">What you get from it</h2>
          <p className="section-subtitle">
            Insights designed for decisions—not just pretty charts.
          </p>
        </div>

        <div className="data-grid">
          <div className="data-card">
            <div className="data-card__title">Sentiment</div>
            <div className="data-card__text">
              See how guests feel (positive/neutral/negative) and what drives it—by
              neighborhood and city.
            </div>
          </div>

          <div className="data-card">
            <div className="data-card__title">Themes & keywords</div>
            <div className="data-card__text">
              We surface the most mentioned topics in reviews so you can spot patterns:
              “quiet”, “clean”, “location”, “check-in”, and more.
            </div>
          </div>

          <div className="data-card">
            <div className="data-card__title">Occupancy signals</div>
            <div className="data-card__text">
              Availability patterns help compare demand across neighborhoods and room
              types—useful for direction, seasonality, and trend spotting.
            </div>
          </div>

          <div className="data-card">
            <div className="data-card__title">Top hosts</div>
            <div className="data-card__text">
              Identify dominant hosts and clusters of competition—great for market
              saturation and benchmarking.
            </div>
          </div>
        </div>
      </section>

      {/* HOW WE DO IT */}
      <section className="section data-split">
        <div className="data-split__left">
          <h2 className="data-split__title">How we process it</h2>
          <p className="data-split__text">
            We keep the workflow consistent across all cities so comparisons stay
            meaningful.
          </p>

          <div className="data-bullets">
            <div className="bullet">
              <div className="bullet-title">Standardize</div>
              <div className="bullet-text">
                City + neighborhood names, coordinates, and data types are normalized so
                the dashboard behaves the same everywhere.
              </div>
            </div>

            <div className="bullet">
              <div className="bullet-title">Clean & validate</div>
              <div className="bullet-text">
                We handle missing values, price parsing, duplicates, and inconsistent
                fields—then run sanity checks before loading.
              </div>
            </div>

            <div className="bullet">
              <div className="bullet-title">Aggregate</div>
              <div className="bullet-text">
                We compute neighborhood summaries (and optionally room-type splits) so
                you can compare areas instantly.
              </div>
            </div>

            <div className="bullet">
              <div className="bullet-title">Enrich with NLP</div>
              <div className="bullet-text">
                Reviews are processed for sentiment and top words/themes so the “why”
                becomes visible, not just the “what”.
              </div>
            </div>
          </div>
        </div>

        <div className="data-split__right">
          <div className="data-callout">
            <div className="data-callout__title">What you can learn</div>
            <div className="data-callout__text">
              <ul className="data-list">
                <li>Which neighborhoods are most loved—and what guests praise.</li>
                <li>Where complaints cluster (noise, cleanliness, check-in, etc.).</li>
                <li>How room types differ across areas (entire home vs private room).</li>
                <li>Where demand appears strongest based on availability signals.</li>
                <li>Which hosts dominate and where competition is concentrated.</li>
              </ul>
            </div>
          </div>

          <div className="data-note">
            <div className="data-note__title">Limitations (real talk)</div>
            <div className="data-note__text">
              Reviews have bias, and availability isn’t the same as confirmed bookings.
              We treat outputs as directional insights and keep processing consistent so
              comparisons stay fair.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
