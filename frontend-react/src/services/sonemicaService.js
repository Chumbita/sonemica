const API_URL = import.meta.env.VITE_API_URL;

export const sonemicaService = {
  sonemicaAnalysis: async (access_token) => {
    const response = await fetch(`${API_URL}/sonemica/analyzer?access_token=${access_token}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Error en el análisis de Sonemica");
    }
    
    const data = await response.json();
    return data;
  },
};