/**
 * TanStack Query hooks. This is the ONLY place server state enters
 * React components -- screens must never fetch directly or hold their
 * own copy of canonical state in local state, per
 * UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 2 ("server-state
 * management") -- the console must never become a second source of
 * truth.
 */
import { useQuery } from "@tanstack/react-query";
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
