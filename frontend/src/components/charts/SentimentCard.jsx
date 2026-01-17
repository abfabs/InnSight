import { useMemo, useState } from "react";
import "../../styles/app.css";

function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function fmtPct(v) {
  const n = toNum(v);
  return `${n.toFixed(1)}%`;
}

export default function SentimentCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;
  const [tip, setTip] = useState(null); // {label, pct, count, x, y}

  if (!row) {
    return (
      <div className="cardbox">
        <div className="card-title-row"><h3>Sentiment</h3></div>
        <div className="muted" style={{ textAlign: "center", padding: "12px 0" }}>No data</div>
      </div>
    );
  }

  const parts = useMemo(() => {
    const total = toNum(row.total_reviews);
    const positivePct = toNum(row.positive);
    const neutralPct = toNum(row.neutral);
    const negativePct = toNum(row.negative);

    const positiveCount = toNum(row.positive_count);
    const neutralCount = toNum(row.neutral_count);
    const negativeCount = toNum(row.negative_count);

    // Real widths
    const real = [
      { key: "positive", label: "Positive", pct: positivePct, count: positiveCount },
      { key: "neutral", label: "Neutral", pct: neutralPct, count: neutralCount },
      { key: "negative", label: "Negative", pct: negativePct, count: negativeCount },
    ];

    // Display widths: make tiny segments visible (purely visual)
    const MIN = 3; // percent of bar
    const positives = real.find((x) => x.key === "positive");
    const smalls = real.filter((x) => x.key !== "positive");

    const displaySmalls = smalls.map((s) => ({
      ...s,
      displayPct: s.pct > 0 ? Math.max(s.pct, MIN) : 0,
    }));
    const usedBySmalls = displaySmalls.reduce((a, b) => a + b.displayPct, 0);

    const displayPositive = Math.max(0, 100 - usedBySmalls);

    return {
      total,
      real,
      display: [
        { ...positives, displayPct: displayPositive },
        ...displaySmalls,
      ],
    };
  }, [row]);

  return (
    <div className="cardbox">
      <div className="card-title-row"><h3>Sentiment</h3></div>

      <div className="row">
        <div className="stat">
          <div className="stat-label">Total reviews</div>
          <div className="stat-value">{row.total_reviews}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Positive</div>
          <div className="stat-value">{row.positive}%</div>
        </div>
        <div className="stat">
          <div className="stat-label">Neutral</div>
          <div className="stat-value">{row.neutral}%</div>
        </div>
        <div className="stat">
          <div className="stat-label">Negative</div>
          <div className="stat-value">{row.negative}%</div>
        </div>
      </div>

      {/* Compact 100% stacked bar */}
      <div className="sent-wrap" onMouseLeave={() => setTip(null)}>
        <div className="sent-bar" role="img" aria-label="Sentiment distribution (100% stacked bar)">
          {parts.display.map((p) => (
            <div
              key={p.key}
              className="sent-seg"
              data-sent={p.key}
              style={{ width: `${p.displayPct}%` }}
              onMouseMove={(e) => {
                const r = e.currentTarget.getBoundingClientRect();
                setTip({
                  label: p.label,
                  pct: p.pct,
                  count: p.count,
                  x: r.left + r.width / 2,
                  y: r.top,
                });
              }}
              title={`${p.label}: ${fmtPct(p.pct)} (${p.count})`}
            />
          ))}
        </div>

        {tip && (
          <div
            className="sent-tooltip"
            style={{ left: tip.x, top: tip.y, transform: "translate(-50%, -10px)" }}
          >
            <div className="sent-tooltip__title">{tip.label}</div>
            <div className="sent-tooltip__row">
              {fmtPct(tip.pct)} <span className="muted">({tip.count})</span>
            </div>
          </div>
        )}

        {/* Callout line to make the small ones feel “important” */}
        <div className="sent-callouts">
          <div className="sent-pill" data-sent="neutral">
            Neutral <strong>{fmtPct(row.neutral)}</strong>
          </div>
          <div className="sent-pill" data-sent="negative">
            Negative <strong>{fmtPct(row.negative)}</strong>
          </div>
        </div>

        <div className="muted sent-note">
          *Small segments are visually widened for readability.
        </div>
      </div>
    </div>
  );
}
