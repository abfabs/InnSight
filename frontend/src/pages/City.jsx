import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchJSON } from "../api/client";
import NeighborhoodFilter from "../components/NeighborhoodFilter";
import MapPanel from "../components/MapPanel";
import DashboardPanel from "../components/DashboardPanel";
import "../styles/app.css";

const CITY_CENTER = {
  amsterdam: [52.3676, 4.9041],
  prague: [50.0755, 14.4378],
  rome: [41.9028, 12.4964],
};

export default function City() {
  const { city } = useParams();

  const [neighborhoods, setNeighborhoods] = useState([]);
  const [neighborhood, setNeighborhood] = useState("");

  const [markers, setMarkers] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [occupancy, setOccupancy] = useState([]);
  const [topHosts, setTopHosts] = useState([]);

  const [loadingMap, setLoadingMap] = useState(true);
  const [loadingDash, setLoadingDash] = useState(true);
  const [err, setErr] = useState("");

  const center = CITY_CENTER[city] || CITY_CENTER.amsterdam;
  const isFiltered = Boolean(neighborhood);
  const level = isFiltered ? "neighborhood" : "city";

  // Reset neighborhood when city changes
  useEffect(() => {
    setNeighborhood("");
  }, [city]);

  // Fetch neighborhoods list
  useEffect(() => {
    let alive = true;
    setErr("");

    fetchJSON(`/api/neighborhoods?city=${city}`)
      .then((data) => {
        if (!alive) return;
        setNeighborhoods(data.neighborhoods || []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
      });

    return () => {
      alive = false;
    };
  }, [city]);

  // Fetch markers when city/neighborhood changes
  useEffect(() => {
    let alive = true;
    setLoadingMap(true);
    setErr("");

    const neighParam = neighborhood ? `&neighborhood=${encodeURIComponent(neighborhood)}` : "";
    const url = `/api/listings-map?city=${city}${neighParam}&limit=50000`;

    fetchJSON(url)
      .then((m) => {
        if (!alive) return;
        setMarkers(m || []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
        setMarkers([]);
      })
      .finally(() => {
        if (!alive) return;
        setLoadingMap(false);
      });

    return () => {
      alive = false;
    };
  }, [city, neighborhood]);

  // Fetch dashboard panels when city/neighborhood changes
  useEffect(() => {
    let alive = true;
    setLoadingDash(true);
    setErr("");

    const neighParam = neighborhood ? `&neighborhood=${encodeURIComponent(neighborhood)}` : "";

    const pSentiment = fetchJSON(`/api/sentiment-summary?city=${city}&level=${level}${neighParam}`);
    const pRoomTypes = fetchJSON(`/api/room-types?city=${city}&level=${level}${neighParam}`);
    const pOccupancy = fetchJSON(`/api/occupancy?city=${city}&level=${level}${neighParam}`);
    const pTopHosts = fetchJSON(`/api/top-hosts?city=${city}&level=${level}${neighParam}`);

    Promise.all([pSentiment, pRoomTypes, pOccupancy, pTopHosts])
      .then(([s, r, o, t]) => {
        if (!alive) return;
        setSentiment(s || []);
        setRoomTypes(r || []);
        setOccupancy(o || []);
        setTopHosts(t || []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
        setSentiment([]);
        setRoomTypes([]);
        setOccupancy([]);
        setTopHosts([]);
      })
      .finally(() => {
        if (!alive) return;
        setLoadingDash(false);
      });

    return () => {
      alive = false;
    };
  }, [city, neighborhood, level]);

  return (
    <div className="page page--city">
      <header className="topbar">
        <div className="topbar-left">
          <Link to="/" className="backlink">← Cities</Link>
          <h2 className="title">{city}</h2>
        </div>

        <NeighborhoodFilter
          neighborhoods={neighborhoods}
          value={neighborhood}
          onChange={setNeighborhood}
        />
      </header>

      {err && <div className="error">{err}</div>}

      <div className="split">
        <div className="panel panel--map">
          {loadingMap ? (
            <div className="loading">Loading map…</div>
          ) : (
            <MapPanel
              markers={markers}
              center={center}
              zoom={12}
              isFiltered={isFiltered}
            />
          )}
        </div>

        <div className="panel panel--dash">
          {loadingDash ? (
            <div className="loading">Loading dashboard…</div>
          ) : (
            <DashboardPanel
              city={city}
              level={level}
              neighborhood={neighborhood}
              sentiment={sentiment}
              roomTypes={roomTypes}
              occupancy={occupancy}
              topHosts={topHosts}
            />
          )}
        </div>
      </div>
    </div>
  );
}
