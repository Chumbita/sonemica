// src/pages/LoadingPage.jsx
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useSonemicaService } from "../hooks/useSonemicaService";

function LoadingPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error, requestAnalysis } = useSonemicaService();
  const [analysisStarted, setAnalysisStarted] = useState(false);

  useEffect(() => {
    // Prevenir múltiples llamadas
    if (analysisStarted) return;

    const performAnalysis = async () => {
      setAnalysisStarted(true);

      // Obtener el token del state o del localStorage
      const accessToken =
        location.state?.accessToken ||
        localStorage.getItem("spotify_access_token");

      if (!accessToken) {
        console.error("No hay access token disponible");
        navigate("/home");
        return;
      }

      try {
        console.log("Iniciando análisis con token:", accessToken);
        const result = await requestAnalysis(accessToken);

        console.log("Análisis completado:", result);

        // Guardar resultados en localStorage
        localStorage.setItem("sonemica_results", JSON.stringify(result));

        // Redirigir a la página de resultados
        navigate("/results", { state: { data: result } });
      } catch (err) {
        console.error("Error en el análisis:", err);
        // Mostrar error en la misma página o redirigir
        alert(`Error: ${err.message}`);
      }
    };

    performAnalysis();
  }, [analysisStarted, location.state, navigate, requestAnalysis]);

  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="spinner"></div>
        <h2>Analizando tu música...</h2>
        <p>Estamos procesando tus datos de Spotify</p>
        <p className="loading-subtext">Esto puede tomar unos segundos</p>

        {error && (
          <div className="error-message">
            <p>❌ Ocurrió un error: {error.message}</p>
            <button onClick={() => navigate("/")}>Volver al inicio</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default LoadingPage;
