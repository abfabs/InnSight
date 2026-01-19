import "maplibre-gl/dist/maplibre-gl.css";
import MapGL from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import { useMemo } from "react";

function quantile(sorted, q) {
  if (!sorted.length) return NaN;
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] === undefined) return sorted[base];
  return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
}

function fmtNum(x, digits = 3) {
  const n = Number(x);
  if (!Number.isFinite(n)) return "–";
  return n.toFixed(digits);
}

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

export default function MapPanel({ markers, viewState, setViewState }) {
  const FULL_CONF_REVIEWS = 10;
  const MIN_CONF_REVIEWS = 1;

  const thresholds = useMemo(() => {
    const rows = Array.isArray(markers) ? markers : [];
    const vals = rows
      .map((p) => Number(p.sentiment_mean))
      .filter((x) => Number.isFinite(x))
      .sort((a, b) => a - b);

    if (vals.length < 50) {
      return { q20: 0.7, q40: 0.8, q60: 0.88, q80: 0.94, sampleSize: vals.length };
    }

    return {
      q20: quantile(vals, 0.2),
      q40: quantile(vals, 0.4),
      q60: quantile(vals, 0.6),
      q80: quantile(vals, 0.8),
      sampleSize: vals.length,
    };
  }, [markers]);

  function baseColorForMean(mean) {
    if (!Number.isFinite(mean)) return [148, 163, 184, 140];
    if (mean <= thresholds.q20) return [220, 38, 38, 210];
    if (mean <= thresholds.q40) return [245, 158, 11, 210];
    if (mean <= thresholds.q60) return [37, 99, 235, 210];
    if (mean <= thresholds.q80) return [34, 197, 94, 210];
    return [22, 163, 74, 210];
  }

  function confidenceFactor(reviewCount) {
    const rc = Number(reviewCount);
    if (!Number.isFinite(rc)) return 0.55;
    const x = (rc - MIN_CONF_REVIEWS) / (FULL_CONF_REVIEWS - MIN_CONF_REVIEWS);
    return clamp(x, 0, 1);
  }

  function alphaForConfidence(conf) {
    return Math.round(90 + conf * 120);
  }

  function radiusForConfidence(conf) {
    return 2.2 + conf * 1.8;
  }

  function bucketLabelForMean(mean) {
    if (!Number.isFinite(mean)) return "No sentiment";
    if (mean <= thresholds.q20) return "Bottom 20% (worst)";
    if (mean <= thresholds.q40) return "20–40%";
    if (mean <= thresholds.q60) return "40–60%";
    if (mean <= thresholds.q80) return "60–80%";
    return "Top 20% (best)";
  }

  const data = useMemo(() => {
    return (markers || [])
      .map((p) => {
        const lat = Number(p.latitude);
        const lon = Number(p.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

        const mean = Number(p.sentiment_mean);
        const conf = confidenceFactor(p.review_count);

        const base = baseColorForMean(mean);
        const color = [base[0], base[1], base[2], alphaForConfidence(conf)];

        return {
          position: [lon, lat],
          color,
          radius: radiusForConfidence(conf),
          bucketLabel: bucketLabelForMean(mean),
          conf,
          listing_name: p.listing_name,
          neighborhood: p.neighborhood,
          room_type: p.room_type,
          price: p.price,
          review_count: p.review_count,
          sentiment_mean: p.sentiment_mean,
          listing_id: p.listing_id,
          city: p.city,
        };
      })
      .filter(Boolean);
  }, [markers, thresholds]);

  const layers = useMemo(() => {
    return [
      new ScatterplotLayer({
        id: "listings",
        data,
        getPosition: (d) => d.position,
        getFillColor: (d) => d.color,
        radiusUnits: "pixels",
        getRadius: (d) => d.radius,
        radiusMinPixels: 2,
        radiusMaxPixels: 7,
        pickable: true,
        autoHighlight: true,
        highlightColor: [255, 255, 255, 180],
      }),
    ];
  }, [data]);

  const getTooltip = useMemo(() => {
    return ({ object }) => {
      if (!object) return null;

      const name = object.listing_name || "Listing";
      const nb = object.neighborhood || "Unknown";
      const room = object.room_type || "–";
      const rc = Number.isFinite(Number(object.review_count)) ? `${Number(object.review_count)}` : "–";

      return {
        text: `${name} • ${nb} • ${rc} reviews • ${room}`,
        style: {
          backgroundColor: "rgba(15, 23, 42, 0.92)",
          color: "#e2e8f0",
          padding: "8px 10px",
          borderRadius: "12px",
          boxShadow: "0 12px 30px rgba(0,0,0,0.35)",
          border: "1px solid rgba(148,163,184,0.18)",
          fontSize: "12px",
          fontWeight: 650,
          whiteSpace: "nowrap",
          maxWidth: "none",
          pointerEvents: "none",
        },
      };
    };
  }, []);

  return (
    <div className="map-canvas">
      <div className="map-clip">
        <DeckGL
          viewState={viewState}
          onViewStateChange={({ viewState: vs }) => setViewState(vs)}
          controller={true}
          layers={layers}
          getTooltip={getTooltip}
          style={{ width: "100%", height: "100%" }}
        >
          <MapGL
            mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
            reuseMaps
            onError={(e) => console.warn("Map error:", e?.error || e)}
          />
        </DeckGL>
      </div>
    </div>
  );
}
