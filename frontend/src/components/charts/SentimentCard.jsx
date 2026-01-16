import { PieChart, Pie, Tooltip } from "recharts";
import "../../styles/app.css";

export default function SentimentCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;

  if (!row) {
    return <div className="cardbox"><h3>Sentiment</h3><div className="muted">No data</div></div>;
  }

  const chartData = [
    { name: "Positive", value: row.positive_count },
    { name: "Neutral", value: row.neutral_count },
    { name: "Negative", value: row.negative_count },
  ];

  return (
    <div className="cardbox">
      <h3>Sentiment</h3>
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

      <div className="chart">
        <PieChart width={320} height={220}>
          <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={90} />
          <Tooltip />
        </PieChart>
      </div>
    </div>
  );
}
