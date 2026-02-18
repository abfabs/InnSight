import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="page page--notfound">
      <div className="notfound">
        <div className="notfound-code">404</div>
        <h1 className="notfound-title">Page not found</h1>
        <p className="notfound-text">
          The page you are looking for doesn’t exist or has been moved.
        </p>
        <Link to="/" className="notfound-link">
          Go back home
        </Link>
      </div>
    </div>
  );
}
