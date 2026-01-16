import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
import City from "./pages/City.jsx";
import Header from "./components/Layout/Header";
import Footer from "./components/Layout/Footer";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <>
      <Header />

      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/city/:city" element={<City />} />
        <Route path="*" element={<NotFound />} />
      </Routes>

      <Footer />
    </>
  );
}
