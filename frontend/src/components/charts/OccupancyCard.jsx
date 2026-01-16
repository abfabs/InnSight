import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import "../../styles/app.css";

export default function OccupancyCard({ data }) {
  const row = Array.isArray(data) && data.length ? data[0] : null;

  if (!row || !row.monthly_occupancy) {
    return <div className="cardbox"><h3>Occupancy</h3><div className="muted">No data</div></div>;
  }

  const chartData = row.monthly_occupancy.map((m) => ({
    month: m.month,
    occupancy_rate: m.occupancy_rate,
  }));

  return (
    <div className="cardbox">
      <h3>Occupancy</h3>
      <div className="chart">
        <LineChart width={360} height={220} data={chartData}>
          <XAxis dataKey="month" hide />
          <YAxis domain={[0, 100]} />
          <Line type="monotone" dataKey="occupancy_rate" />
          <Tooltip />
        </LineChart>
      </div>
    </div>
  );
}
