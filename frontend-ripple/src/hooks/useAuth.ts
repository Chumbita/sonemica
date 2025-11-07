import { track, effect } from "ripple";
import { apiGet } from "../services/api";

export type AuthStatus = {
  connected: boolean;
  user?: { id: string; displayName?: string };
};

export function useAuth() {
  const loading = track(true as boolean);
  const error   = track(undefined as string | undefined);
  const data    = track({ connected: false } as AuthStatus);

  async function fetchStatus() {
    try {
      @loading = true;
      const res = await apiGet<AuthStatus>("/api/auth/status");
      @data = res;
      @error = undefined;
    } catch (e: any) {
      @data = { connected: false };
      @error = e?.message ?? "Error";
    } finally {
      @loading = false;
    }
  }

  effect(() => { fetchStatus(); });

  return { data, loading, error, refetch: fetchStatus };
}
