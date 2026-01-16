import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJSON } from "../api/client";
import CityCard from "../components/CityCard";
import "../styles/app.css";

const CITY_IMAGES = {
  amsterdam: "/images/cities/amsterdam.jpg",
  rome: "/images/cities/rome.jpg",
  prague: "/images/cities/prague.jpg",
};

const CITY_ORDER = ["amsterdam", "rome", "prague"];

export default function Landing() {
  const nav = useNavigate();
  const [cities, setCities] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    let alive = true;
    fetchJSON("/api/cities")
      .then((data) => {
        if (!alive) return;
        setCities(data.cities || []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
      });
    return () => {
      alive = false;
    };
  }, []);

  const orderedCities = useMemo(() => {
    return cities
      .slice()
      .sort((a, b) => {
        const ai = CITY_ORDER.indexOf(String(a).toLowerCase());
        const bi = CITY_ORDER.indexOf(String(b).toLowerCase());
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      });
  }, [cities]);

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-inner">
          <p className="hero-kicker">InnSight</p>
          <h1 className="hero-title">Beyond the listing.</h1>
          <p className="hero-subtitle">
            Explore listings, sentiment, occupancy, and neighborhood patterns—
            city by city.
          </p>

          <div className="hero-actions">
            <button className="btn btn-primary" onClick={() => nav("#cities")}>
              Explore cities
            </button>
            <button className="btn btn-ghost" onClick={() => nav("/city/amsterdam")}>
              Open demo city
            </button>
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat__value">3</div>
              <div className="hero-stat__label">Cities</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat__value">NLP</div>
              <div className="hero-stat__label">Sentiment insights</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat__value">Geo</div>
              <div className="hero-stat__label">Neighborhood context</div>
            </div>
          </div>
        </div>
      </section>

      <div className="page">
        {err && <div className="error">{err}</div>}

        <section id="cities" className="section">
          <div className="section-head">
            <h2 className="section-title">Explore cities</h2>
            <p className="section-subtitle">
              Jump into a city and browse neighborhood-level insights.
            </p>
          </div>

          <div className="grid">
            {orderedCities.map((city) => {
              const key = String(city).toLowerCase();
              return (
                <CityCard
                  key={city}
                  title={city}
                  imageUrl={CITY_IMAGES[key]}
                  onClick={() => nav(`/city/${key}`)}
                />
              );
            })}
          </div>
        </section>

        <section id="data" className="section">
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

        <section id="technology" className="section">
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
                Load listing + review datasets, normalize and clean.
              </div>
            </div>
            <div className="step">
              <div className="step-num">02</div>
              <div className="step-title">Analyze</div>
              <div className="step-text">
                NLP sentiment + aggregation by city and neighborhood.
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
        </section>

        <section id="contact" className="section section-contact">
          <div className="contact-card">
            <h2 className="section-title">Contact</h2>
            <p className="section-subtitle">
              Want a walkthrough or more cities added? Reach out.
            </p>
            <div className="contact-row">
              <span className="contact-label">Email</span>
              <span className="contact-value">your@email.com</span>
            </div>
            <div className="contact-row">
              <span className="contact-label">GitHub</span>
              <span className="contact-value">github.com/abfabs/InnSight</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
