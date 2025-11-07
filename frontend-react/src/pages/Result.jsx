// src/pages/ResultsPage.jsx
import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);

  useEffect(() => {
    // Intentar obtener los datos del state o del localStorage
    const data =
      location.state?.data ||
      JSON.parse(localStorage.getItem("sonemica_results") || "null");

    if (!data) {
      // Si no hay datos, redirigir al inicio
      navigate("/home");
      return;
    }

    setResults(data);
  }, [location.state, navigate]);

  if (!results) {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }}>
        Cargando resultados...
      </div>
    );
  }

  return (
    <div className="results-container">
      <h1>🎵 Tus Resultados de Sonemica</h1>

      <div className="results-content">
        {/* Aquí renderizas tus resultados según la estructura de tu API */}
        {/* Por ahora muestro el JSON formateado */}
        <pre className="results-json">{JSON.stringify(results, null, 2)}</pre>
      </div>

      <button className="back-button" onClick={() => navigate("/")}>
        ← Volver al inicio
      </button>
    </div>
  );
}

export default ResultsPage;
