import { useState } from "react";
import { sonemicaService } from "../services/sonemicaService";

export const useSonemicaService = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const requestAnalysis = async (access_token) => {
    setLoading(true);
    setError(null);

    try {
      const response = await sonemicaService.sonemicaAnalysis(access_token);
      return response;
    } catch (error) {
      setError(error);
      throw error; 
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    requestAnalysis,
  };
};