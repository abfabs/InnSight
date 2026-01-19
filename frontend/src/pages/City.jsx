import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchJSON } from "../api/client";
import NeighborhoodFilter from "../components/NeighborhoodFilter";
import MapPanel from "../components/MapPanel";
import MapLegend from "../components/MapLegend";
import DashboardPanel from "../components/DashboardPanel";

const CITY_CENTER = {
  amsterdam: { lat: 52.3676, lon: 4.9041, zoom: 11.5 },
  prague: { lat: 50.0755, lon: 14.4378, zoom: 11.5 },
  rome: { lat: 41.9028, lon: 12.4964, zoom: 11.3 },
};

// ✅ normalize accents + spacing + dash variants (Dubeč -> dubec)
function normName(s) {
  return String(s || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-");
}

// crude but solid: infer zoom from bounds span
function zoomForBounds(minLat, maxLat, minLon, maxLon, fallback = 13) {
  const latSpan = Math.max(0.000001, maxLat - minLat);
  const lonSpan = Math.max(0.000001, maxLon - minLon);
  const span = Math.max(latSpan, lonSpan);

  if (span < 0.01) return 15;
  if (span < 0.03) return 14;
  if (span < 0.08) return 13;
  if (span < 0.2) return 12;
  return fallback;
}

export default function City() {
  const { city } = useParams();

  const [neighborhoods, setNeighborhoods] = useState([]);
  const [neighborhood, setNeighborhood] = useState("");

  const [markers, setMarkers] = useState([]);

  const [sentiment, setSentiment] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [occupancy, setOccupancy] = useState([]);
  const [topHosts, setTopHosts] = useState([]);

  const [neighSentiment, setNeighSentiment] = useState([]);

  const [loadingMap, setLoadingMap] = useState(true);
  const [loadingDash, setLoadingDash] = useState(true);
  const [err, setErr] = useState("");

  const cityCfg = CITY_CENTER[city] || CITY_CENTER.amsterdam;
  const level = neighborhood ? "neighborhood" : "city";

  const [viewState, setViewState] = useState(() => ({
    longitude: cityCfg.lon,
    latitude: cityCfg.lat,
    zoom: cityCfg.zoom,
    bearing: 0,
    pitch: 0,
  }));

  // Reset neighborhood + view when city changes
  useEffect(() => {
    setNeighborhood("");
    setViewState((v) => ({
      ...v,
      longitude: cityCfg.lon,
      latitude: cityCfg.lat,
      zoom: cityCfg.zoom,
      bearing: 0,
      pitch: 0,
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  // Fetch ALL markers ONLY when city changes
  useEffect(() => {
    let alive = true;
    setLoadingMap(true);
    setErr("");

    fetchJSON(`/api/listings-map?city=${city}&limit=50000`)
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
  }, [city]);

  // Fetch neighborhood sentiment once per city
  useEffect(() => {
    let alive = true;
    setErr("");

    fetchJSON(`/api/neighborhood-sentiment?city=${city}`)
      .then((rows) => {
        if (!alive) return;
        setNeighSentiment(rows || []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
        setNeighSentiment([]);
      });

    return () => {
      alive = false;
    };
  }, [city]);

  // Fly to neighborhood bounds when selected
  const boundsByNeighborhood = useMemo(() => {
    const map = new globalThis.Map();
    for (const m of markers || []) {
      const nb = normName(m.neighborhood);
      if (!nb) continue;

      const lat = Number(m.latitude);
      const lon = Number(m.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;

      const b = map.get(nb) || { minLat: lat, maxLat: lat, minLon: lon, maxLon: lon };

      b.minLat = Math.min(b.minLat, lat);
      b.maxLat = Math.max(b.maxLat, lat);
      b.minLon = Math.min(b.minLon, lon);
      b.maxLon = Math.max(b.maxLon, lon);

      map.set(nb, b);
    }
    return map;
  }, [markers]);

  useEffect(() => {
    if (!neighborhood) {
      setViewState((v) => ({
        ...v,
        longitude: cityCfg.lon,
        latitude: cityCfg.lat,
        zoom: cityCfg.zoom,
        transitionDuration: 600,
      }));
      return;
    }

    const b = boundsByNeighborhood.get(normName(neighborhood));
    if (!b) return;

    const lat = (b.minLat + b.maxLat) / 2;
    const lon = (b.minLon + b.maxLon) / 2;
    const z = zoomForBounds(b.minLat, b.maxLat, b.minLon, b.maxLon, 13);

    setViewState((v) => ({
      ...v,
      longitude: lon,
      latitude: lat,
      zoom: z,
      transitionDuration: 700,
    }));
  }, [neighborhood, boundsByNeighborhood, cityCfg.lat, cityCfg.lon, cityCfg.zoom]);

  // Dashboard fetch
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
          {loadingMap && <div className="loading loading--overlay">Loading map…</div>}

          <MapLegend />

          <div className="map-fill">
            <MapPanel markers={markers} viewState={viewState} setViewState={setViewState} />
          </div>
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
