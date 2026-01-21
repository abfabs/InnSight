import { Link, NavLink } from "react-router-dom";
import "./Header.css";

export default function Header() {
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
          <NavLink to="/" className="nav__link">
            Home
          </NavLink>
          <a href="#data" className="nav__link">
            Data
          </a>
          <a href="#technology" className="nav__link">
            Technology
          </a>
          <a href="#technology" className="nav__link">
            About
          </a>
          <a href="#contact" className="nav__link">
            Contact
          </a>
        </nav>
      </div>
    </header>
  );
}
