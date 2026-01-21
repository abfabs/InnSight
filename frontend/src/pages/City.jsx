import { useEffect, useMemo, useState, useDeferredValue } from "react";
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

// normalize accents + spacing + dash variants
function normName(s) {
  return (s ?? "")
    .toString()
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-");
}

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

function parsePrice(v) {
  if (v === null || v === undefined) return NaN;
  if (typeof v === "number") return Number.isFinite(v) ? v : NaN;

  const s = String(v).trim();
  if (!s) return NaN;

  const cleaned = s.replace(/[^\d.,-]/g, "");
  if (!cleaned) return NaN;

  let normalized = cleaned;
  const hasComma = normalized.includes(",");
  const hasDot = normalized.includes(".");

  if (hasComma && hasDot) normalized = normalized.replace(/,/g, "");
  else if (hasComma && !hasDot) {
    const parts = normalized.split(",");
    if (parts.length === 2 && parts[1].length <= 2) normalized = parts[0] + "." + parts[1];
    else normalized = normalized.replace(/,/g, "");
  }

  const n = Number(normalized);
  return Number.isFinite(n) ? n : NaN;
}

// --- PAN/ZOOM (restore the old “fit neighborhood bounds” behavior) ---
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

// Dual-handle slider (no dependency): 2 overlapped range inputs
function DualRangeSlider({ min, max, step = 5, value, onChange }) {
  const [minVal, maxVal] = value;

  const safeMin = clamp(minVal, min, maxVal);
  const safeMax = clamp(maxVal, safeMin, max);

  const minPct = ((safeMin - min) / (max - min || 1)) * 100;
  const maxPct = ((safeMax - min) / (max - min || 1)) * 100;

  return (
    <div className="dual-range" style={{ "--minPct": `${minPct}%`, "--maxPct": `${maxPct}%` }}>
      <div className="dual-range__track" />
      <div className="dual-range__range" />

      <input
        className="dual-range__input dual-range__input--min"
        type="range"
        min={min}
        max={max}
        step={step}
        value={safeMin}
        onChange={(e) => onChange([Math.min(Number(e.target.value), safeMax), safeMax])}
      />

      <input
        className="dual-range__input dual-range__input--max"
        type="range"
        min={min}
        max={max}
        step={step}
        value={safeMax}
        onChange={(e) => onChange([safeMin, Math.max(Number(e.target.value), safeMin)])}
      />

      <div className="dual-range__values">
        <span>Min: {safeMin}</span>
        <span>Max: {safeMax}</span>
      </div>
    </div>
  );
}

export default function City() {
  const { city } = useParams();
  const cityKey = normName(city);
  const cityCfg = CITY_CENTER[cityKey] || { lat: 51.5074, lon: -0.1278, zoom: 11.5 };

  const [err, setErr] = useState("");

  const [neighborhoods, setNeighborhoods] = useState([]);
  const [neighborhood, setNeighborhood] = useState("");

  const [markers, setMarkers] = useState([]);
  const [loadingMap, setLoadingMap] = useState(true);

  const [sentiment, setSentiment] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [occupancy, setOccupancy] = useState([]);
  const [topHosts, setTopHosts] = useState([]);
  const [loadingDash, setLoadingDash] = useState(true);

  const [viewState, setViewState] = useState(() => ({
    longitude: cityCfg.lon,
    latitude: cityCfg.lat,
    zoom: cityCfg.zoom,
    bearing: 0,
    pitch: 0,
  }));

  // ---- Filters ----
  const [roomTypeSet, setRoomTypeSet] = useState(new Set()); // empty => all

  const [priceBounds, setPriceBounds] = useState([0, 500]);
  const [priceDraft, setPriceDraft] = useState([0, 500]); // instant
  const [priceRange, setPriceRange] = useState([0, 500]); // debounced (applied)

  const level = neighborhood ? "neighborhood" : "city";
  const neighParam = neighborhood ? `&neighborhood=${encodeURIComponent(neighborhood)}` : "";

  function toggleRoomType(type) {
    setRoomTypeSet((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }

  function clearRoomTypes() {
    setRoomTypeSet(new Set());
  }

  // Reset neighborhood + view when city changes
  useEffect(() => {
    setNeighborhood("");
    setRoomTypeSet(new Set());
    setViewState((v) => ({
      ...v,
      longitude: cityCfg.lon,
      latitude: cityCfg.lat,
      zoom: cityCfg.zoom,
      bearing: 0,
      pitch: 0,
      transitionDuration: 600,
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city]);

  // Fetch neighborhoods list (NOTE: your API returns { neighborhoods: [...] })
  useEffect(() => {
    let alive = true;
    setErr("");

    fetchJSON(`/api/neighborhoods?city=${city}`)
      .then((data) => {
        if (!alive) return;
        setNeighborhoods(Array.isArray(data?.neighborhoods) ? data.neighborhoods : []);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(String(e.message || e));
        setNeighborhoods([]);
      });

    return () => {
      alive = false;
    };
  }, [city]);

  // Fetch map markers (your real endpoint)
  useEffect(() => {
    let alive = true;
    setErr("");
    setLoadingMap(true);

    fetchJSON(`/api/listings-map?city=${city}&limit=50000`)
      .then((data) => {
        if (!alive) return;
        setMarkers(Array.isArray(data) ? data : Array.isArray(data?.rows) ? data.rows : []);
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

  // ✅ Restore the old “fly to neighborhood bounds” logic (from previous file)
  const boundsByNeighborhood = useMemo(() => {
    const map = new globalThis.Map();

    for (const m of markers || []) {
      const nb = normName(m?.neighborhood);
      if (!nb) continue;

      const lat = Number(m?.latitude);
      const lon = Number(m?.longitude);
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

  // Fetch dashboard data (your real endpoints)
  useEffect(() => {
    let alive = true;
    setErr("");
    setLoadingDash(true);

    Promise.all([
      fetchJSON(`/api/neighborhood-sentiment?city=${city}`),
      fetchJSON(`/api/sentiment-summary?city=${city}&level=${level}${neighParam}`),
      fetchJSON(`/api/room-types?city=${city}&level=${level}${neighParam}`),
      fetchJSON(`/api/occupancy?city=${city}&level=${level}${neighParam}`),
      fetchJSON(`/api/top-hosts?city=${city}&level=${level}${neighParam}`),
    ])
      .then(([nbSent, sentSum, rt, occ, hosts]) => {
        if (!alive) return;
        setSentiment(Array.isArray(nbSent) ? nbSent : []);
        setRoomTypes(Array.isArray(rt) ? rt : []);
        setOccupancy(Array.isArray(occ) ? occ : []);
        setTopHosts(Array.isArray(hosts) ? hosts : []);
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
  }, [city, neighborhood, level, neighParam]);

  // Build available room types from markers for the chips
  const availableRoomTypes = useMemo(() => {
    const s = new Set();
    (markers || []).forEach((m) => {
      if (m?.room_type) s.add(m.room_type);
    });
    return Array.from(s).sort();
  }, [markers]);

  // Detect price bounds once per city load (from ALL markers)
  const detectedPriceBounds = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;

    for (const m of markers || []) {
      const p = parsePrice(m?.price);
      if (!Number.isFinite(p)) continue;
      if (p < min) min = p;
      if (p > max) max = p;
    }

    if (!Number.isFinite(min) || !Number.isFinite(max)) return [0, 500];
    const minR = Math.floor(min / 10) * 10;
    const maxR = Math.ceil(max / 10) * 10;
    return [minR, maxR];
  }, [markers]);

  // Sync bounds and clamp current slider values
  useEffect(() => {
    setPriceBounds(detectedPriceBounds);

    setPriceDraft((prev) => {
      const [bMin, bMax] = detectedPriceBounds;
      const [pMin, pMax] = prev;
      const defaultish = pMin === 0 && (pMax === 500 || pMax === 0);
      if (defaultish) return [bMin, bMax];
      return [Math.max(bMin, pMin), Math.min(bMax, pMax)];
    });

    setPriceRange((prev) => {
      const [bMin, bMax] = detectedPriceBounds;
      const [pMin, pMax] = prev;
      const defaultish = pMin === 0 && (pMax === 500 || pMax === 0);
      if (defaultish) return [bMin, bMax];
      return [Math.max(bMin, pMin), Math.min(bMax, pMax)];
    });
  }, [detectedPriceBounds]);

  // Debounce: apply draft to map after user pauses dragging
  useEffect(() => {
    const t = setTimeout(() => setPriceRange(priceDraft), 180);
    return () => clearTimeout(t);
  }, [priceDraft]);

  // Filter markers for the map (use debounced priceRange)
  const filteredMarkers = useMemo(() => {
    const [minP, maxP] = priceRange;

    return (markers || []).filter((m) => {
      const nbOk = !neighborhood || normName(m?.neighborhood) === normName(neighborhood);
      const rtOk = roomTypeSet.size === 0 || roomTypeSet.has(m?.room_type);

      const p = parsePrice(m?.price);
      const priceOk = !Number.isFinite(p) ? true : p >= minP && p <= maxP;

      return nbOk && rtOk && priceOk;
    });
  }, [markers, neighborhood, roomTypeSet, priceRange]);

  // Defer heavy map updates to keep UI responsive
  const deferredMarkers = useDeferredValue(filteredMarkers);

  return (
    <div className="page page--city">
      <header className="topbar">
        <div className="topbar-left">
          <Link to="/" className="backlink">
            ← Cities
          </Link>
          <h2 className="title">{city}</h2>
        </div>

        <NeighborhoodFilter neighborhoods={neighborhoods} value={neighborhood} onChange={setNeighborhood} />
      </header>

      {err && <div className="error">{err}</div>}

      <div className="split">
        <div className="panel panel--map">
          <div className="map-filters">
            <div className="map-filters__row">
              <div className="map-filters__label">Room type</div>
              <div className="chip-row">
                <button
                  type="button"
                  className={`chip ${roomTypeSet.size === 0 ? "chip--on" : ""}`}
                  onClick={clearRoomTypes}
                >
                  All
                </button>

                {availableRoomTypes.map((t) => (
                  <button
                    key={t}
                    type="button"
                    className={`chip ${roomTypeSet.has(t) ? "chip--on" : ""}`}
                    onClick={() => toggleRoomType(t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="map-filters__row">
              <div className="map-filters__label">
                Price range: {priceDraft[0]} – {priceDraft[1]}
              </div>

              <DualRangeSlider
                min={priceBounds[0]}
                max={priceBounds[1]}
                step={5}
                value={priceDraft}
                onChange={setPriceDraft}
              />
            </div>

            <div className="map-filters__meta">
              Showing <b>{filteredMarkers.length}</b> / {markers.length} listings
            </div>
          </div>

          {loadingMap && <div className="loading loading--overlay">Loading map…</div>}

          <MapPanel markers={deferredMarkers} allMarkers={markers} viewState={viewState} setViewState={setViewState} />

          <MapLegend />
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
