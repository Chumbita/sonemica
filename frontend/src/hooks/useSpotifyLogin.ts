import { goToSpotifyLogin } from "../services/api";

/**
 * Hook que maneja el flujo de login con Spotify.
 * 
 * El backend expone un endpoint `/api/auth/login` que redirige a Spotify
 * y luego vuelve a la URL indicada con ?redirect=...
 * 
 * Por defecto, redirige a `/loading` tras el login.
 */
export function useSpotifyLogin() {
  /** Inicia el proceso de login con Spotify */
  function start(redirectTo = "/loading") {
    goToSpotifyLogin(redirectTo);
  }

  return { start };
}
