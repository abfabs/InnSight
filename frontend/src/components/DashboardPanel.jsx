import SentimentCard from "./charts/SentimentCard";
import RoomTypesCard from "./charts/RoomTypesCard";
import OccupancyCard from "./charts/OccupancyCard";
import TopHostsCard from "./charts/TopHostsCard";
import "../styles/app.css";

export default function DashboardPanel({ city, level, neighborhood, sentiment, roomTypes, occupancy, topHosts }) {
  const title = neighborhood ? `${city} • ${neighborhood}` : `${city} • City`;

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
