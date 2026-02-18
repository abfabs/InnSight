import { useMemo, useState } from "react";

function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function fmtInt(v) {
  return Math.round(toNum(v)).toLocaleString();
}

function fmtPct(v) {
  const n = toNum(v);
  return `${n.toFixed(1)}%`;
}

function norm(v) {
  return String(v ?? "").trim().toLowerCase();
}

export default function SentimentCard({ data, neighborhood }) {
  const [tip, setTip] = useState(null); // {label, pct, count, x, y}

  const row = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) return null;

    // If API already filtered it, behave like the other cards
    if (data.length === 1) return data[0];

    const nb = norm(neighborhood);

    // If a neighborhood is selected, prefer that row
    if (nb) {
      const nbRow =
        data.find((r) => norm(r?.neighborhood) === nb) ||
        data.find((r) => norm(r?.neighbourhood) === nb); // just in case spelling differs

      if (nbRow) return nbRow;
    }

    // Otherwise prefer city aggregate
    const cityRow =
      data.find(
        (r) =>
          r?.level === "city" &&
          (r?.neighborhood === null || r?.neighborhood === undefined)
      ) || data.find((r) => r?.level === "city");

    if (cityRow) return cityRow;

    // Fallback: biggest total_reviews
    return data
      .slice()
      .sort((a, b) => toNum(b?.total_reviews) - toNum(a?.total_reviews))[0];
  }, [data, neighborhood]);

  const parts = useMemo(() => {
    if (!row) return { total: 0, real: [], display: [] };

    const real = [
      {
        key: "positive",
        label: "Positive",
        pct: toNum(row.positive),
        count: toNum(row.positive_count),
      },
      {
        key: "neutral",
        label: "Neutral",
        pct: toNum(row.neutral),
        count: toNum(row.neutral_count),
      },
      {
        key: "negative",
        label: "Negative",
        pct: toNum(row.negative),
        count: toNum(row.negative_count),
      },
    ];

    // Visual-only widening of small segments
    const MIN = 3;
    const positives = real.find((x) => x.key === "positive") || real[0];
    const smalls = real.filter((x) => x.key !== "positive");

    const displaySmalls = smalls.map((s) => ({
      ...s,
      displayPct: s.pct > 0 ? Math.max(s.pct, MIN) : 0,
    }));

    const usedBySmalls = displaySmalls.reduce((a, b) => a + b.displayPct, 0);
    const displayPositive = Math.max(0, 100 - usedBySmalls);

    return {
      total: toNum(row.total_reviews),
      real,
      display: [{ ...positives, displayPct: displayPositive }, ...displaySmalls],
    };
  }, [row]);

  if (!row) {
    return (
      <div className="cardbox">
        <div className="card-title-row">
          <h3>Sentiment Analysis</h3>
        </div>
        <div className="muted" style={{ textAlign: "center", padding: "12px 0" }}>
          No data
        </div>
      </div>
    );
  }

  return (
    <div className="cardbox">
      <div className="card-title-row">
        <h3>Sentiment Analysis</h3>
      </div>

      <div className="row">
        <div className="stat">
          <div className="stat-label">Total reviews</div>
          <div className="stat-value">{fmtInt(row.total_reviews)}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Positive</div>
          <div className="stat-value">{fmtPct(row.positive)}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Neutral</div>
          <div className="stat-value">{fmtPct(row.neutral)}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Negative</div>
          <div className="stat-value">{fmtPct(row.negative)}</div>
        </div>
      </div>

      <div className="sent-wrap" onMouseLeave={() => setTip(null)}>
        <div
          className="sent-bar"
          role="img"
          aria-label="Sentiment distribution (100% stacked bar)"
        >
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
              title={`${p.label}: ${fmtPct(p.pct)} (${fmtInt(p.count)})`}
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
              {fmtPct(tip.pct)} <span className="muted">({fmtInt(tip.count)})</span>
            </div>
          </div>
        )}

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
