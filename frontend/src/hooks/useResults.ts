import { track, effect } from "ripple";
import { apiGet } from "../services/api";

export type Slide = { title: string; text: string; /* + campos del gráfico */ };
export type Results = { slides: Slide[] };

export function useResults(jobId?: string) {
  const loading = track(false as boolean);
  const error   = track(undefined as string | undefined);
  const data    = track(undefined as Results | undefined);

  async function fetchResults(id: string) {
    try {
      @loading = true;
      const res = await apiGet<Results>(`/api/analysis/results?jobId=${encodeURIComponent(id)}`);
      @data = res;
      @error = undefined;
    } catch (e: any) {
      @error = e?.message ?? "No se pudieron obtener resultados";
    } finally {
      @loading = false;
    }
  }

  effect(() => {
    if (jobId) fetchResults(jobId);
  });

  return { loading, error, data, refetch: fetchResults };
}
