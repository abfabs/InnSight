import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
import City from "./pages/City.jsx";
import Data from "./pages/Data.jsx";
import About from "./pages/About.jsx";
import Technology from "./pages/Technology.jsx";
import Contact from "./pages/Contact.jsx";
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
        <Route path="/data" element={<Data />} />
        <Route path="/about" element={<About />} />
        <Route path="/technology" element={<Technology />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Footer />
    </>
  );
}
