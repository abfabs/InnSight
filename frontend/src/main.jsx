import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./styles/base.css";
import "./styles/city.css";
import "./styles/landing.css";
import "./styles/pages.css";
import "./styles/chat.css";
import "leaflet/dist/leaflet.css";
import "./map/leafletIcons";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
