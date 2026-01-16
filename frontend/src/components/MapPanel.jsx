import { MapContainer, TileLayer, CircleMarker, useMap } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { useEffect, useMemo } from "react";
import L from "leaflet";

function sentimentColor(cat) {
  if (cat === "positive") return "#16a34a";  // green
  if (cat === "neutral") return "#2563eb"; // blue
  if (cat === "negative") return "#dc2626"; // red
  return "#94a3b8"; // gray fallback
}

function FitToMarkers({ points, center, zoom, shouldFit }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    // Only fit bounds when filtering (neighborhood selected)
    if (!shouldFit) {
      map.setView(center, zoom);
      return;
    }

    if (!points.length) {
      map.setView(center, zoom);
      return;
    }

    const bounds = L.latLngBounds(points.map((p) => [p.lat, p.lng]));
    map.fitBounds(bounds, { padding: [30, 30], maxZoom: 15 });
  }, [map, points, center, zoom, shouldFit]);

  return null;
}

export default function MapPanel({ markers, center, zoom, isFiltered }) {
  const points = useMemo(() => {
    return (markers || [])
      .map((m) => {
        const lat = Number(m.latitude);
        const lng = Number(m.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
        return { ...m, lat, lng };
      })
      .filter(Boolean);
  }, [markers]);

  return (
    <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FitToMarkers points={points} center={center} zoom={zoom} shouldFit={isFiltered} />

      <MarkerClusterGroup chunkedLoading>
        {points.map((m) => (
          <CircleMarker
            key={m.listing_id}
            center={[m.lat, m.lng]}
            radius={4}
            pathOptions={{
              color: sentimentColor(m.sentiment_category),
              fillColor: sentimentColor(m.sentiment_category),
              fillOpacity: 0.9,
              weight: 1,
            }}
          />
        ))}
      </MarkerClusterGroup>
    </MapContainer>
  );
}
