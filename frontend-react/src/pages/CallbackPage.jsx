import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

function CallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  useEffect(() => {
    const processCallback = async () => {
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const expiresIn = searchParams.get('expires_in');
      
      if (accessToken) {
        // Guardar tokens
        localStorage.setItem('spotify_access_token', accessToken);
        localStorage.setItem('spotify_refresh_token', refreshToken);
        
        // Calcular tiempo de expiración
        const expirationTime = Date.now() + (parseInt(expiresIn) * 1000);
        localStorage.setItem('spotify_token_expiration', expirationTime.toString());
        
        console.log('Token guardado:', accessToken);
        
        // Redirigir a loading con el proceso de análisis
        navigate('/loading', { state: { accessToken } });
      } else {
        // Manejar error
        console.error('No se recibió access_token');
        navigate('/');
      }
    };

    processCallback();
  }, [searchParams, navigate]);
  
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      gap: '1rem'
    }}>
      <h2>Autenticando con Spotify...</h2>
      <p>Por favor espera un momento</p>
    </div>
  );
}

export default CallbackPage;