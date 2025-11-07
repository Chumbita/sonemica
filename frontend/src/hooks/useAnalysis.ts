import { track } from "ripple";
import { apiPost } from "../services/api";

type StartAnalysisRes = {
  jobId: string;
};

export function useAnalysis() {
  const loading = track(false as boolean);
  const error   = track(undefined as string | undefined);
  const jobId   = track(undefined as string | undefined);

  async function start() {
    try {
      @loading = true;
      const res = await apiPost<StartAnalysisRes>("/api/analysis/start");
      @jobId = res.jobId;
      @error = undefined;
      return res.jobId;
    } catch (e: any) {
      @error = e?.message ?? "No se pudo iniciar el análisis";
      return undefined;
    } finally {
      @loading = false;
    }
  }

  return { loading, error, jobId, start };
}
