import "../styles/app.css";

export default function Technology() {
  return (
    <div className="page tech-page">
      {/* HERO */}
      <section className="section tech-hero" id="technology">
        <div className="tech-hero__inner">
          <p className="tech-badge">TECHNOLOGY</p>
          <h1 className="tech-title">How it works</h1>
          <p className="tech-subtitle">
            InnSight is an end-to-end pipeline: ingest raw city datasets, clean and
            enrich them, then serve interactive insights through a fast API and a
            modern dashboard.
          </p>

          <div className="tech-flow">
            <div className="tech-flow__card">
              <div className="tech-flow__top">
                <span className="tech-flow__num">01</span>
                <span className="tech-flow__pill">ETL</span>
              </div>
              <div className="tech-flow__title">Ingest</div>
              <div className="tech-flow__text">
                Pull listings, reviews, and availability per city. Normalize formats
                and validate data integrity before loading.
              </div>
            </div>

            <div className="tech-flow__card">
              <div className="tech-flow__top">
                <span className="tech-flow__num">02</span>
                <span className="tech-flow__pill">NLP</span>
              </div>
              <div className="tech-flow__title">Analyze</div>
              <div className="tech-flow__text">
                Process review text into sentiment + keywords, then aggregate
                metrics by neighborhood and room type.
              </div>
            </div>

            <div className="tech-flow__card">
              <div className="tech-flow__top">
                <span className="tech-flow__num">03</span>
                <span className="tech-flow__pill">API</span>
              </div>
              <div className="tech-flow__title">Serve</div>
              <div className="tech-flow__text">
                Store processed outputs in MongoDB and expose them through a
                REST API designed for fast reads.
              </div>
            </div>

            <div className="tech-flow__card">
              <div className="tech-flow__top">
                <span className="tech-flow__num">04</span>
                <span className="tech-flow__pill">UI</span>
              </div>
              <div className="tech-flow__title">Explore</div>
              <div className="tech-flow__text">
                Maps and dashboard cards visualize neighborhood insights so users
                can compare cities quickly and consistently.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DIAGRAM */}
      <section className="section">
        <div className="section-head tech-head">
          <h2 className="section-title">Architecture</h2>
          <p className="section-subtitle">
            A simple overview of how data moves through InnSight.
          </p>
        </div>

        <div className="arch">
          <div className="arch-col">
            <div className="arch-label">Inputs</div>

            <div className="arch-box">
              <div className="arch-title">Raw datasets</div>
              <div className="arch-text">
                Listings • Reviews • Calendar/Availability
              </div>
            </div>

            <div className="arch-box arch-muted">
              <div className="arch-title">City scope</div>
              <div className="arch-text">
                Each city is processed independently for consistent outputs.
              </div>
            </div>
          </div>

          <div className="arch-mid">
            <div className="arch-arrow" />
            <div className="arch-arrow" />
          </div>

          <div className="arch-col">
            <div className="arch-label">Processing</div>

            <div className="arch-box">
              <div className="arch-title">ETL & normalization</div>
              <div className="arch-text">
                Parse fields, clean prices, standardize neighborhoods, remove duplicates.
              </div>
            </div>

            <div className="arch-box">
              <div className="arch-title">NLP enrichment</div>
              <div className="arch-text">
                Sentiment scoring, keyword extraction, and aggregation by neighborhood.
              </div>
            </div>

            <div className="arch-box arch-muted">
              <div className="arch-title">Quality checks</div>
              <div className="arch-text">
                Validation steps to keep metrics stable and comparable across cities.
              </div>
            </div>
          </div>

          <div className="arch-mid">
            <div className="arch-arrow" />
            <div className="arch-arrow" />
          </div>

          <div className="arch-col">
            <div className="arch-label">Outputs</div>

            <div className="arch-box">
              <div className="arch-title">MongoDB</div>
              <div className="arch-text">
                Aggregated collections optimized for dashboard queries.
              </div>
            </div>

            <div className="arch-box">
              <div className="arch-title">Flask REST API</div>
              <div className="arch-text">
                Lightweight endpoints for city, neighborhood, and metric views.
              </div>
            </div>

            <div className="arch-box">
              <div className="arch-title">React + Map UI</div>
              <div className="arch-text">
                Interactive city pages, maps, and comparison cards.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* STACK */}
      <section className="section tech-split">
        <div className="tech-split__left">
          <h2 className="tech-split__title">Tech stack</h2>
          <p className="tech-split__text">
            A pragmatic stack chosen for reliability and performance in a data-heavy app.
          </p>

          <div className="tech-stack">
            <div className="stack-item">
              <div className="stack-title">Backend</div>
              <div className="stack-text">
                Python + Flask for the REST API. MongoDB for storage and fast aggregated reads.
              </div>
            </div>

            <div className="stack-item">
              <div className="stack-title">Frontend</div>
              <div className="stack-text">
                React + Vite for the UI. MapLibre for mapping and interactive layers.
              </div>
            </div>

            <div className="stack-item">
              <div className="stack-title">Analytics</div>
              <div className="stack-text">
                NLP pipeline, sentiment aggregation, and ETL scripts to generate neighborhood summaries.
              </div>
            </div>
          </div>
        </div>

        <div className="tech-split__right">
          <div className="tech-callout">
            <div className="tech-callout__title">Behind the scenes</div>
            <ul className="tech-list">
              <li>Raw datasets are cleaned and standardized per city.</li>
              <li>Reviews are processed into sentiment and top keywords.</li>
              <li>Metrics are aggregated into neighborhood-level documents.</li>
              <li>The API serves small responses for fast UI updates.</li>
            </ul>
          </div>

          <div className="tech-note">
            <div className="tech-note__title">Built to scale</div>
            <div className="tech-note__text">
              Adding a new city is primarily a data + ETL task. Once processed, the same
              API routes and frontend components can display it immediately.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
