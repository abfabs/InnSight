import "../styles/app.css";

export default function MapLegend() {
    return (
        <div className="map-legend-top">
            <div className="map-legend-top-title">Listing sentiment</div>

            <div className="map-legend-top-row">
                <span className="dot dot-green" /> Top 20%
                <span className="dot dot-blue" /> 60–80%
                <span className="dot dot-mint" /> 40–60%
                <span className="dot dot-amber" /> 20–40%
                <span className="dot dot-red" /> Bottom 20%
            </div>

            <div className="map-legend-top-note">
                Color = sentiment quintile · Size & Opacity = review count
            </div>
        </div>
    );
}
