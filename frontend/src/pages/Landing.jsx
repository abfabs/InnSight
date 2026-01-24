import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJSON } from "../api/client";
import CityCard from "../components/CityCard";
import "../styles/app.css";

const CITY_IMAGES = {
  amsterdam: "/images/cities/amsterdam.jpg",
  rome: "/images/cities/rome.jpg",
  prague: "/images/cities/prague.jpg",
  sicily: "/images/cities/sicily.jpg",
  bordeaux: "/images/cities/bordeaux.jpg",
  crete: "/images/cities/crete.jpg",
};

// Exactly this order (top row then bottom row)
const CITY_ORDER = ["amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"];

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

  const scrollToCities = () => {
    const el = document.getElementById("cities");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-inner">
          <p className="hero-kicker">InnSight</p>
          <h1 className="hero-title">Beyond the listing.</h1>
          <p className="hero-subtitle">
            Explore listings, sentiment, occupancy, and neighborhood patterns—city by city.
          </p>

          <div className="hero-actions">
            <button className="btn btn-primary" onClick={scrollToCities}>
              Explore cities
            </button>
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat__value">6</div>
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

          <div className="grid grid--cities">
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
      </div>
    </div>
  );
}
