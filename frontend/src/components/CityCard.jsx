import "../styles/app.css";

export default function CityCard({ title, imageUrl, onClick }) {
  return (
    <button className="card" onClick={onClick}>
      <div className="card-img" style={{ "--bg": `url(${imageUrl})` }}>
        <div className="card-title-overlay">{title}</div>
      </div>
    </button>
  );
}


