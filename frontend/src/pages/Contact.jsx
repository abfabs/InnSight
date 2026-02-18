import { useState } from "react";

// Netlify expects url-encoded form bodies
function encode(data) {
  return Object.keys(data)
    .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(data[k])}`)
    .join("&");
}

export default function Contact() {
  const [status, setStatus] = useState("idle"); // idle | sending | success | error
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
    "bot-field": "",
  });

  function onChange(e) {
    const { name, value } = e.target;
    setForm((p) => ({ ...p, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setStatus("sending");

    try {
      const body = encode({
        "form-name": "contact",
        ...form,
      });

      const res = await fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!res.ok) throw new Error(`Submit failed: ${res.status}`);

      setStatus("success");
      setForm({ name: "", email: "", subject: "", message: "", "bot-field": "" });
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  }

  return (
    <div className="page contact-page">
      {/* CONTACT STRIP */}
      <section className="section section-contact-wide" id="contact">
        <div className="contact-wide">
          <div className="contact-wide-grid">
            {/* LEFT: text + repo/email stacked */}
            <div className="contact-wide-left">
              <p className="contact-badge">CONTACT</p>
              <h2 className="contact-title">Get in touch</h2>
              <p className="contact-subtitle">
                Interested in the data, want to explore new cities, or have ideas
                for extending the platform? We’re always open to collaboration,
                feedback, and discussion.
              </p>

              {/* Repository + Email (stacked) */}
              <div className="contact-wide-actions contact-wide-actions--stack">
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

            {/* RIGHT: contact card */}
            <div className="contact-wide-right">
              <div className="contact-form-card">
                <div className="contact-form-head">
                  <h3 className="contact-form-title">Send a message</h3>
                  <p className="contact-form-subtitle">
                    We usually reply within 1–2 days.
                  </p>
                </div>

                <form
                  className="contact-form"
                  name="contact"
                  method="POST"
                  data-netlify="true"
                  netlify-honeypot="bot-field"
                  onSubmit={onSubmit}
                >
                  {/* required for Netlify */}
                  <input type="hidden" name="form-name" value="contact" />

                  {/* honeypot */}
                  <p className="contact-honeypot">
                    <label>
                      Don’t fill this out:
                      <input
                        name="bot-field"
                        value={form["bot-field"]}
                        onChange={onChange}
                      />
                    </label>
                  </p>

                  <div className="contact-form-row">
                    <label className="contact-field">
                      <span className="contact-field-label">Name</span>
                      <input
                        className="contact-input"
                        type="text"
                        name="name"
                        value={form.name}
                        onChange={onChange}
                        required
                        autoComplete="name"
                      />
                    </label>

                    <label className="contact-field">
                      <span className="contact-field-label">Email</span>
                      <input
                        className="contact-input"
                        type="email"
                        name="email"
                        value={form.email}
                        onChange={onChange}
                        required
                        autoComplete="email"
                      />
                    </label>
                  </div>

                  <label className="contact-field">
                    <span className="contact-field-label">Subject</span>
                    <input
                      className="contact-input"
                      type="text"
                      name="subject"
                      value={form.subject}
                      onChange={onChange}
                      placeholder="Optional"
                    />
                  </label>

                  <label className="contact-field">
                    <span className="contact-field-label">Message</span>
                    <textarea
                      className="contact-textarea"
                      name="message"
                      rows={5}
                      value={form.message}
                      onChange={onChange}
                      required
                    />
                  </label>

                  <div className="contact-form-actions">
                    <button
                      className="contact-btn"
                      type="submit"
                      disabled={status === "sending"}
                    >
                      {status === "sending" ? "Sending..." : "Send message"}
                    </button>

                    {status === "success" && (
                      <span className="contact-form-status contact-success">
                        Sent — thank you!
                      </span>
                    )}
                    {status === "error" && (
                      <span className="contact-form-status contact-error">
                        Something went wrong — try again.
                      </span>
                    )}
                  </div>
                </form>
              </div>
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
