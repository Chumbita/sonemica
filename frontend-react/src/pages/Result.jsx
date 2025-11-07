import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/globals.css";
import "../styles/results.css";

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);

  useEffect(() => {
    // Cargar datos desde state o localStorage
    const data =
      location.state?.data ||
      JSON.parse(localStorage.getItem("sonemica_results") || "null");

    if (!data) {
      navigate("/home");
      return;
    }

    setResults(data);
  }, [location.state, navigate]);

  if (!results) {
    return (
      <div className="results-root">
        <div className="slide-container">
          <p className="placeholder">Cargando resultados...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-root bg-grid">
      <div className="slides">
        <section className="slide">
          <div className="slide-container">
            <div>
              <h2 className="slide-title gradient-text">
                🎵 Tus resultados de Sonemica
              </h2>
              <p className="slide-text">
                A continuacion, explora como se ve tu huella sonora.
              </p>
              <pre className="slide-text placeholder">
                {JSON.stringify(results, null, 2)}
              </pre>
            </div>

            <div className="slide-visual">
              <span className="placeholder">Visualización pendiente</span>
            </div>
          </div>
        </section>
      </div>

      <div className="results-wrap" style={{ textAlign: "center" }}>
        <button className="btn-primary" onClick={() => navigate("/home")}>
          ← Volver al inicio
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;