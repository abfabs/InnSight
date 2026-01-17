import { useMemo, useState } from "react";
import "../../styles/app.css";

function clampPct(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

// Largest remainder + ensure non-zero pct gets at least 1 dot
function allocateDots(items) {
  const raw = items.map((it) => ({ ...it, pct: clampPct(it.pct) }));

  const floors = raw.map((it) => Math.floor(it.pct));
  const remainders = raw
    .map((it, i) => ({ i, r: it.pct - floors[i] }))
    .sort((a, b) => b.r - a.r);

  const dots = floors.slice();
  let used = dots.reduce((a, b) => a + b, 0);

  // min 1 dot for non-zero categories
  for (let i = 0; i < raw.length; i++) {
    if (raw[i].pct > 0 && dots[i] === 0) {
      dots[i] = 1;
      used += 1;
    }
  }

  // if over 100, remove from biggest categories first (never remove forced 1-dot mins)
  if (used > 100) {
    const order = raw.map((it, i) => ({ i, pct: it.pct })).sort((a, b) => b.pct - a.pct);
    let k = 0;
    while (used > 100) {
      const idx = order[k].i;
      if (!(raw[idx].pct > 0 && dots[idx] === 1) && dots[idx] > 0) {
        dots[idx] -= 1;
        used -= 1;
      }
      k = (k + 1) % order.length;
    }
  }

  // add remaining to reach 100
  let j = 0;
  while (used < 100) {
    const idx = remainders[j].i;
    dots[idx] += 1;
    used += 1;
    j = (j + 1) % remainders.length;
  }

  return raw.map((it, i) => ({ ...it, dots: dots[i] }));
}

function toneForRoomType(label) {
  if (label === "Entire home/apt") return "positive";
  if (label === "Private room") return "neutral";
  if (label === "Hotel room") return "neutral2";
  if (label === "Shared room") return "negative";
  return "neutral";
}

export default function RoomTypesCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;
  const [tip, setTip] = useState(null); // {x,y,label,pct,count}

  if (!row) {
    return (
      <div className="cardbox">
        <div className="card-title-row"><h3>Room types</h3></div>
        <div className="muted" style={{ textAlign: "center", padding: "12px 0" }}>No data</div>
      </div>
    );
  }

  const entries = useMemo(() => {
    const rt = row.room_types || {};
    const arr = Object.entries(rt).map(([k, v]) => ({
      key: k,
      label: k,
      pct: clampPct(v?.percentage),
      count: Number(v?.count) || 0,
      tone: toneForRoomType(k),
    }));
    arr.sort((a, b) => b.pct - a.pct);
    return allocateDots(arr);
  }, [row]);

  const dotOwners = useMemo(() => {
    const out = [];
    for (const e of entries) {
      for (let i = 0; i < e.dots; i++) out.push(e);
    }
    return out.slice(0, 100);
  }, [entries]);

  // 100 dots as a thick half-donut: 4 rows x 25 columns
  const ROWS = 4;
  const COLS = 25; // 4 * 25 = 100
  const W = 260;
  const H = 140;

  // Draw TOP half (cap): center near bottom, arc goes across the top area
  const cx = W / 2;
  const cy = 120;

  const rOuter = 92;
  const rStep = 10; // gap between rings
  const dotR = 4.2;

  return (
    <div className="cardbox">
      <div className="card-title-row"><h3>Room types</h3></div>

      <div className="muted" style={{ textAlign: "center", marginBottom: 8 }}>
        Total listings: {row.total_listings}
      </div>

      <div className="rt-donut-wrap" onMouseLeave={() => setTip(null)}>
        <svg
          className="rt-donut"
          width={W}
          height={H}
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Room type distribution as a dotted semi-donut (100 dots, each dot is 1%)"
        >
          {Array.from({ length: 100 }, (_, idx) => {
            const rowIdx = Math.floor(idx / COLS);
            const colIdx = idx % COLS;

            const t = colIdx / (COLS - 1);
            const a = 0 + (Math.PI - 0) * t; 

            const r = rOuter - rowIdx * rStep;
            const x = cx + r * Math.cos(a);
            const y = cy - r * Math.sin(a); 

            const m = dotOwners[idx];
            const tone = m?.tone || "neutral";
            const label = m?.label || "Unknown";
            const pct = m?.pct ?? 0;
            const count = m?.count ?? 0;

            return (
              <circle
                key={idx}
                cx={x}
                cy={y}
                r={dotR}
                className="rt-donut-dot"
                data-tone={tone}
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTip({
                    x: rect.left + rect.width / 2,
                    y: rect.top,
                    label,
                    pct,
                    count,
                  });
                }}
                onMouseMove={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTip((prev) => (prev ? { ...prev, x: rect.left + rect.width / 2, y: rect.top } : prev));
                }}
              />
            );
          })}
        </svg>

        {tip && (
          <div
            className="rt-donut-tooltip"
            style={{ left: tip.x, top: tip.y, transform: "translate(-50%, -10px)" }}
          >
            <div className="rt-donut-tooltip__title">{tip.label}</div>
            <div className="rt-donut-tooltip__row">
              {Number(tip.pct).toFixed(1)}% <span className="muted">({tip.count})</span>
            </div>
          </div>
        )}
      </div>

      <div className="rt-donut-legend">
        {entries.map((e) => (
          <div key={e.key} className="rt-donut-legend-item">
            <span className="rt-donut-swatch" data-tone={e.tone} />
            <span className="rt-donut-legend-label">{e.label}</span>
            <span className="rt-donut-legend-val">{e.pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
