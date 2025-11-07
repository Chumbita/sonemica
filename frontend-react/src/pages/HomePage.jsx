import React from "react";
import { useNavigate } from "react-router-dom";
import HeaderBar from "../components/HeaderBar";
import "../styles/HomePage.module.css"

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="container">
      <div className="page-bg" aria-hidden="true" />

      <HeaderBar />

      <section className="hero">
        <h1 className="hero-title gradient-text">
          {"Descubrí tu identidad sonora"}
        </h1>
        <p className="hero-desc">
          {
            "Sonemica transforma tu música en arte dinámico. Conectá tu Spotify y descubrí cómo evoluciona tu energía sonora con el tiempo."
          }
        </p>
        <div className="hero-actions">
          <button
            onClick={() =>
              (window.location.href =
                "https://accounts.spotify.com/es/authorize?client_id=9fb6a73637f343218b39eb34a09660ca&response_type=code&redirect_uri=http://127.0.0.1:8000/api/auth/spotify/callback&scope=user-read-recently-played%20user-top-read&show_dialog=true")
            }
          >
            Acceder con Spotify
          </button>
        </div>
      </section>
    </div>
  );
}
