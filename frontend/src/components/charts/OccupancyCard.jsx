import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import "../../styles/app.css";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function parseYearMonth(s) {
  const m = String(s ?? "").trim().match(/^(\d{4})-(\d{2})$/);
  if (!m) return null;
  const monthIndex = Number(m[2]) - 1; // 0..11
  if (monthIndex < 0 || monthIndex > 11) return null;
  return monthIndex;
}

function fmtPct(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "";
  return `${Math.round(n)}%`;
}

function OccupancyTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const val = payload[0]?.value;

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__title">{label}</div>
      <div className="chart-tooltip__row">
        Occupancy: <strong>{fmtPct(val)}</strong>
      </div>
    </div>
  );
}

export default function OccupancyCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;
  const monthly = row?.monthly_occupancy;

  const hasMonthly = Array.isArray(monthly) && monthly.length > 0;

  // Aggregate across years: average occupancy per month (Jan..Dec)
  const sums = Array(12).fill(0);
  const counts = Array(12).fill(0);

  if (hasMonthly) {
    for (const r of monthly) {
      const mi = parseYearMonth(r.month);
      const occ = Number(r.occupancy_rate);
      if (mi === null || !Number.isFinite(occ)) continue;
      sums[mi] += occ;
      counts[mi] += 1;
    }
  }

  const chartData = MONTHS.map((m, i) => ({
    month: m,
    occupancy: counts[i] ? sums[i] / counts[i] : 0,
  }));

  return (
    <div className="cardbox">
      <div className="card-title-row">
        <h3>Occupancy</h3>
      </div>

      {!hasMonthly ? (
        <div className="muted" style={{ textAlign: "center", padding: "18px 0" }}>
          No data
        </div>
      ) : (
        <div className="chart chart--bar" style={{ width: "100%", height: 290, minHeight: 290 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, bottom: 32, left: 0 }}>
              <defs>
                <linearGradient id="occGradient" x1="0" y1="1" x2="0" y2="0">
                  <stop offset="0%" stopColor="rgba(54, 87, 255, 0.18)" />
                  <stop offset="60%" stopColor="rgba(54, 87, 255, 0.55)" />
                  <stop offset="100%" stopColor="rgba(54, 87, 255, 0.9)" />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 6" vertical={false} opacity={0.2} />

              <XAxis
                dataKey="month"
                interval={0}
                tickLine={false}
                axisLine={false}
                height={50}
                tickMargin={12}
                tick={{ fontSize: 12 }}
                angle={-35}
                textAnchor="end"
              />

              <YAxis
                domain={[0, 100]}
                tickFormatter={fmtPct}
                tickLine={false}
                axisLine={false}
                width={44}
                tick={{ fontSize: 12 }}
              />

              <Tooltip content={<OccupancyTooltip />} cursor={false} />

              <Bar
                dataKey="occupancy"
                fill="url(#occGradient)"
                radius={[6, 6, 2, 2]}
                barSize={16}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
