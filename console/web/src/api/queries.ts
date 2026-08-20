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

export const useRunComparison = (fromRunId: string | undefined, toRunId: string | undefined) =>
  useQuery({
    queryKey: ["run-comparison", fromRunId ?? null, toRunId ?? null],
    queryFn: () => api.runs.compare(fromRunId as string, toRunId as string),
    enabled: Boolean(fromRunId && toRunId && fromRunId !== toRunId),
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
 * Triggers a real compiler run. On success it invalidates every query
 * that run could have changed -- state, nodes, frontier, audits,
 * chainlink, fc005, runs, ledger -- so the UI reflects the new
 * canonical state within one refetch cycle, never a stale cached view
 * papering over what just happened on disk.
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

// ---- Phase 7: Hypothesis Engine ----

export const useHypotheses = (filters?: { target_node_id?: string; status?: string }) =>
  useQuery({
    queryKey: ["hypotheses", filters ?? {}],
    queryFn: () => api.hypotheses.list(filters),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

export const useHypothesis = (id: string | undefined) =>
  useQuery({
    queryKey: ["hypothesis", id],
    queryFn: () => api.hypotheses.get(id as string),
    enabled: Boolean(id),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

export const useCreateHypothesis = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.hypotheses.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hypotheses"] });
      queryClient.invalidateQueries({ queryKey: ["frontier"] });  // historical_failure_rate can change
    },
  });
};

// ---- Phase 8: Proof / Falsification Workspaces ----

export const useProofs = () =>
  useQuery({ queryKey: ["proofs"], queryFn: api.proofs.list, staleTime: DEFAULT_STALE_TIME_MS });

export const useProof = (nodeId: string | undefined) =>
  useQuery({
    queryKey: ["proof", nodeId],
    queryFn: () => api.proofs.get(nodeId as string),
    enabled: Boolean(nodeId),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

export const useFalsifications = () =>
  useQuery({ queryKey: ["falsifications"], queryFn: api.falsifications, staleTime: DEFAULT_STALE_TIME_MS });

// ---- Phase 9: Literature Workspace ----

export const useLiteratureSources = () =>
  useQuery({ queryKey: ["literature-sources"], queryFn: api.literature.sources, staleTime: DEFAULT_STALE_TIME_MS });

export const useLiteratureItems = () =>
  useQuery({ queryKey: ["literature-items"], queryFn: api.literature.items, staleTime: DEFAULT_STALE_TIME_MS });

export const useLiteratureCrosswalk = (nodeId?: string) =>
  useQuery({
    queryKey: ["literature-crosswalk", nodeId ?? null],
    queryFn: () => api.literature.crosswalk(nodeId),
    staleTime: DEFAULT_STALE_TIME_MS,
  });

export const useLiteratureRecoveries = () =>
  useQuery({ queryKey: ["literature-recoveries"], queryFn: api.literature.recoveries, staleTime: DEFAULT_STALE_TIME_MS });

export const useTransitionHypothesis = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, req }: { id: string; req: { new_status: string; reason: string } }) =>
      api.hypotheses.transition(id, req),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["hypotheses"] });
      queryClient.invalidateQueries({ queryKey: ["hypothesis", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["frontier"] });
    },
  });
};
