import SentimentCard from "./charts/SentimentCard";
import RoomTypesCard from "./charts/RoomTypesCard";
import OccupancyCard from "./charts/OccupancyCard";
import TopHostsCard from "./charts/TopHostsCard";
import "../styles/app.css";

function formatCity(name) {
  if (!name) return "";
  return name
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function DashboardPanel({
  city,
  level,
  neighborhood,
  sentiment,
  roomTypes,
  occupancy,
  topHosts,
}) {
  const cityLabel = formatCity(city);
  const title = neighborhood
    ? `${cityLabel} • ${neighborhood}`
    : `${cityLabel} • City`;

  return (
    <div className="dash">
      <div className="dash-title">{title}</div>

      <div className="dash-stack">
        <SentimentCard data={sentiment} />
        <RoomTypesCard data={roomTypes} />
        <OccupancyCard data={occupancy} />
        <TopHostsCard data={topHosts} />
      </div>
    </div>
  );
}
