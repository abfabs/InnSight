import { Link, NavLink } from "react-router-dom";
import "./Header.css";

export default function Header({ onNewChat }) {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link to="/" className="brand">
          <img
            className="brand__logo"
            src="/images/logo.png"
            alt="InnSight logo"
          />
          <div className="brand__text">
            <div className="brand__name">InnSight</div>
            <div className="brand__tagline">beyond the listing.</div>
          </div>
        </Link>

        <nav className="nav">
          <NavLink to="/" className="nav__link">Home</NavLink>
          <NavLink to="/data" className="nav__link">Data</NavLink>
          <NavLink to="/technology" className="nav__link">Technology</NavLink>
          <NavLink to="/about" className="nav__link">About</NavLink>
          <NavLink to="/contact" className="nav__link">Contact</NavLink>
        </nav>

        <button
          className="chat-new"
          onClick={onNewChat}
          type="button"
          title="New chat"
        >
          New chat
        </button>
      </div>
    </header>
  );
}
