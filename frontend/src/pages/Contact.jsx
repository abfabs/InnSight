import "../styles/app.css";

export default function Contact() {
  return (
    <div className="page contact-page">
      {/* CONTACT STRIP */}
      <section className="section section-contact-wide" id="contact">
        <div className="contact-wide">
          <div className="contact-wide-left">
            <p className="contact-badge">CONTACT</p>
            <h2 className="contact-title">Get in touch</h2>
            <p className="contact-subtitle">
              Interested in the data, want to explore new cities, or have ideas for
              extending the platform? We’re always open to collaboration,
              feedback, and discussion.
            </p>
          </div>

          {/* SINGLE ROW: repo left, email right */}
          <div className="contact-wide-actions">
            <div className="contact-action">
              <span className="contact-label">Repository</span>
              <a
                className="contact-value contact-link"
                href="https://github.com/abfabs/InnSight"
                target="_blank"
                rel="noopener noreferrer"
              >
                github.com/abfabs/InnSight
              </a>
            </div>

            <div className="contact-action">
              <span className="contact-label">Email</span>
              <a
                className="contact-value contact-link"
                href="mailto:innsightbeyond@gmail.com"
              >
                innsightbeyond@gmail.com
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* TEAM */}
      <section className="section">
        <div className="section-head">
          <h2 className="section-title">Team</h2>
          <p className="section-subtitle">
            Built by a multidisciplinary team across engineering, data, and machine learning.
          </p>
        </div>

        <div className="team-grid">
          {/* ALBA */}
          <a
            href="https://github.com/abfabs"
            target="_blank"
            rel="noopener noreferrer"
            className="team-card"
          >
            <div className="team-icon-wrap">
              <img src="/images/icons/tiger.png" alt="Tiger" className="team-icon" />
            </div>
            <div className="team-name">Alba Eftimi</div>
            <div className="team-role">Project Lead • Full-Stack Developer</div>
            <div className="team-desc">
              System architecture, backend API development, database design, end-to-end data
              integration, ML, and product UI.
            </div>
          </a>

          {/* SOKOL */}
          <a
            href="https://github.com/sokolgj19"
            target="_blank"
            rel="noopener noreferrer"
            className="team-card"
          >
            <div className="team-icon-wrap">
              <img src="/images/icons/dolphin.png" alt="Dolphin" className="team-icon" />
            </div>
            <div className="team-name">Sokol Gjeka</div>
            <div className="team-role">Frontend Developer</div>
            <div className="team-desc">
              Interactive map implementation, UI/UX design, JavaScript visualization.
            </div>
          </a>

          {/* RENIS */}
          <a
            href="https://github.com/renisv"
            target="_blank"
            rel="noopener noreferrer"
            className="team-card"
          >
            <div className="team-icon-wrap">
              <img src="/images/icons/crow.png" alt="Crow" className="team-icon" />
            </div>
            <div className="team-name">Renis Vukaj</div>
            <div className="team-role">Data Engineer</div>
            <div className="team-desc">
              ETL pipelines, data cleaning, CSV processing, GeoJSON integration.
            </div>
          </a>

          {/* KEVIN */}
          <a
            href="https://github.com/kevin10v"
            target="_blank"
            rel="noopener noreferrer"
            className="team-card"
          >
            <div className="team-icon-wrap">
              <img src="/images/icons/lion.png" alt="Lion" className="team-icon" />
            </div>
            <div className="team-name">Kevin Voka</div>
            <div className="team-role">ML Engineer</div>
            <div className="team-desc">
              Word cloud generation, sentiment analysis, NLP model training.
            </div>
          </a>
        </div>
      </section>
    </div>
  );
}
