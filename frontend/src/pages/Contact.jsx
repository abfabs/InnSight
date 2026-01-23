import "../styles/app.css";

export default function Contact() {
  return (
    <div className="page">
      <section className="section section-contact" id="contact">
        <div className="contact-card">
          <h2 className="section-title">Contact</h2>
          <p className="section-subtitle">
            Want a walkthrough or more cities added? Reach out.
          </p>

          <div className="contact-row">
            <span className="contact-label">Email</span>
            <span className="contact-value">email@email.com</span>
          </div>

          <div className="contact-row">
            <span className="contact-label">GitHub</span>
            <span className="contact-value">github.com/abfabs/InnSight</span>
          </div>
        </div>
      </section>
    </div>
  );
}
