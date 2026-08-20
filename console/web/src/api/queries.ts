/**
 * TanStack Query hooks. This is the ONLY place server state enters
 * React components -- screens must never fetch directly or hold their
 * own copy of canonical state in local state, per
 * UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 2 ("server-state
 * management") -- the console must never become a second source of
 * truth.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

// Canonical state can change between two requests only via a real
// compiler run (Phase 6+); a short-but-nonzero staleTime avoids
// hammering the API on every re-render while still reflecting a
// fresh run within seconds of it completing.
const DEFAULT_STALE_TIME_MS = 5_000;

export const useHealth = () =>
  useQuery({ queryKey: ["health"], queryFn: api.health, staleTime: DEFAULT_STALE_TIME_MS });

export const useStateRollup = () =>
  useQuery({ queryKey: ["state"], queryFn: api.state, staleTime: DEFAULT_STALE_TIME_MS });

export const useMdcl = () =>
  useQuery({ queryKey: ["mdcl"], queryFn: api.mdcl, staleTime: DEFAULT_STALE_TIME_MS });

export const useNodes = () =>
  useQuery({ queryKey: ["nodes"], queryFn: api.nodes, staleTime: DEFAULT_STALE_TIME_MS });

export const useNode = (id: string | undefined) =>
  useQuery({
    queryKey: ["node", id],
    queryFn: () => api.node(id as string),
    enabled: Boolean(id),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

export const useFrontier = () =>
  useQuery({ queryKey: ["frontier"], queryFn: api.frontier, staleTime: DEFAULT_STALE_TIME_MS });

export const useAudits = () =>
  useQuery({ queryKey: ["audits"], queryFn: api.audits, staleTime: DEFAULT_STALE_TIME_MS });

export const useChainlink = () =>
  useQuery({ queryKey: ["chainlink"], queryFn: api.chainlink, staleTime: DEFAULT_STALE_TIME_MS });

export const useFc005 = () =>
  useQuery({ queryKey: ["fc005"], queryFn: api.fc005, staleTime: DEFAULT_STALE_TIME_MS });

export const useRuns = () =>
  useQuery({ queryKey: ["runs"], queryFn: api.runs.list, staleTime: DEFAULT_STALE_TIME_MS });

export const useRun = (runId: string | undefined) =>
  useQuery({
    queryKey: ["run", runId],
    queryFn: () => api.runs.get(runId as string),
    enabled: Boolean(runId),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

// Ledger is polled, not pushed -- there is no websocket/SSE
// infrastructure here (per the brief's "do not introduce unnecessary
// infrastructure if a simpler architecture is sufficient"), so a
// short refetchInterval is what "live tail" means in this app: the
// Execution screen's ledger panel visibly updates within a few seconds
// of a run completing, without the user reloading the page.
export const useLedger = (limit = 50) =>
  useQuery({
    queryKey: ["ledger", limit],
    queryFn: () => api.ledger(limit),
    staleTime: 2_000,
    refetchInterval: 3_000,
  });

/**
 * The one mutation in the whole app. On success it invalidates every
 * query that a real compiler run could have changed -- state, nodes,
 * frontier, audits, chainlink, fc005, runs, ledger -- so the UI
 * reflects the new canonical state within one refetch cycle, never a
 * stale cached view papering over what just happened on disk.
 */
export const useCreateRun = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.runs.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["state"] });
      queryClient.invalidateQueries({ queryKey: ["nodes"] });
      queryClient.invalidateQueries({ queryKey: ["node"] });
      queryClient.invalidateQueries({ queryKey: ["frontier"] });
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      queryClient.invalidateQueries({ queryKey: ["chainlink"] });
      queryClient.invalidateQueries({ queryKey: ["fc005"] });
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["ledger"] });
    },
  });
};
