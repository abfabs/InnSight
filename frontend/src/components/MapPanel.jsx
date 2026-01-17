import "maplibre-gl/dist/maplibre-gl.css";
import MapGL from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import { useMemo } from "react";

// ✅ normalize accents + spacing + dash variants
function normName(s) {
  return String(s || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove accents (Dubeč -> dubec)
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-");
}

// ✅ color by negative% thresholds
function colorForNeighborhoodRow(row) {
  if (!row) return [148, 163, 184, 160]; // gray if we couldn't match

  const n = Number(row.total_reviews);
  const neg = Number(row.negative);
  const pos = Number(row.positive);
  const mean = Number(row.sentiment_mean);

  // low data => muted
  if (Number.isFinite(n) && n < 10) return [120, 140, 170, 130];

  // Prefer bucket thresholds when available
  if (Number.isFinite(neg) && Number.isFinite(pos)) {
    if (neg >= 10) return [220, 38, 38, 210]; // red
    if (neg >= 5) return [245, 158, 11, 210]; // amber
    if (pos >= 85) return [22, 163, 74, 210]; // green
    return [37, 99, 235, 210]; // blue (mixed)
  }

  // Fallback to mean (your data looks 0..1)
  if (Number.isFinite(mean)) {
    if (mean < 0.65) return [220, 38, 38, 210];
    if (mean < 0.80) return [245, 158, 11, 210];
    if (mean < 0.92) return [37, 99, 235, 210];
    return [22, 163, 74, 210];
  }

  return [148, 163, 184, 160];
}

export default function MapPanel({
  markers,
  neighborhoodSentiment,
  viewState,
  setViewState,
}) {
  const rowByNeighborhood = useMemo(() => {
    const m = new globalThis.Map();
    const rows = Array.isArray(neighborhoodSentiment) ? neighborhoodSentiment : [];
    for (const r of rows) {
      const k = normName(r.neighborhood);
      if (k) m.set(k, r);
    }
    return m;
  }, [neighborhoodSentiment]);

  const data = useMemo(() => {
    return (markers || [])
      .map((p) => {
        const lat = Number(p.latitude);
        const lon = Number(p.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

        const nbKey = normName(p.neighborhood);
        const row = rowByNeighborhood.get(nbKey);

        return {
          position: [lon, lat],
          color: colorForNeighborhoodRow(row),
        };
      })
      .filter(Boolean);
  }, [markers, rowByNeighborhood]);

  const layers = useMemo(() => {
    return [
      new ScatterplotLayer({
        id: "listings",
        data,
        getPosition: (d) => d.position,
        getFillColor: (d) => d.color,
        radiusUnits: "pixels",
        getRadius: 3.5,
        radiusMinPixels: 2,
        radiusMaxPixels: 6,
        pickable: false,
      }),
    ];
  }, [data]);

  // 👇 IMPORTANT: wrapper must have real size
  return (
    <div className="map-canvas">
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: vs }) => setViewState(vs)}
        controller={true}
        layers={layers}
        style={{ width: "100%", height: "100%" }}
      >
        <MapGL
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          reuseMaps
          // prevents resize edge cases from exploding on some GPUs/layouts
          onError={(e) => console.warn("Map error:", e?.error || e)}
        />
      </DeckGL>
    </div>
  );
}
