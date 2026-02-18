import { Routes, Route } from "react-router-dom";
import { useCallback, useRef } from "react";

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
  const chatResetRef = useRef(null);

  const handleNewChat = useCallback(() => {
    chatResetRef.current?.();
  }, []);

  return (
    <>
      <Header onNewChat={handleNewChat} />

      <Routes>
        <Route path="/" element={<Landing chatResetRef={chatResetRef} />} />
        <Route path="/city/:city" element={<City chatResetRef={chatResetRef} />} />
        <Route path="/data" element={<Data chatResetRef={chatResetRef} />} />
        <Route path="/about" element={<About chatResetRef={chatResetRef} />} />
        <Route path="/technology" element={<Technology chatResetRef={chatResetRef} />} />
        <Route path="/contact" element={<Contact chatResetRef={chatResetRef} />} />
        <Route path="*" element={<NotFound />} />
      </Routes>

      <Footer />
    </>
  );
}
