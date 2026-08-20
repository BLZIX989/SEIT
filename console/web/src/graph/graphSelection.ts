import type { NodeSummary } from "../api/types";

/** All transitive dependencies of `id` (its full ancestor set in the DAG). */
export function collectAncestors(id: string, nodesById: Map<string, NodeSummary>): Set<string> {
  const seen = new Set<string>();
  const stack = [...(nodesById.get(id)?.dependencies ?? [])];
  while (stack.length) {
    const cur = stack.pop() as string;
    if (seen.has(cur)) continue;
    seen.add(cur);
    for (const dep of nodesById.get(cur)?.dependencies ?? []) stack.push(dep);
  }
  return seen;
}

/** All transitive dependents of `id` (its full descendant set in the DAG). */
export function collectDescendants(id: string, reverseDeps: Map<string, string[]>): Set<string> {
  const seen = new Set<string>();
  const stack = [...(reverseDeps.get(id) ?? [])];
  while (stack.length) {
    const cur = stack.pop() as string;
    if (seen.has(cur)) continue;
    seen.add(cur);
    for (const dep of reverseDeps.get(cur) ?? []) stack.push(dep);
  }
  return seen;
}

export function buildReverseDeps(nodes: NodeSummary[]): Map<string, string[]> {
  const rev = new Map<string, string[]>();
  for (const n of nodes) {
    for (const dep of n.dependencies) {
      const list = rev.get(dep) ?? [];
      list.push(n.id);
      rev.set(dep, list);
    }
  }
  return rev;
}
