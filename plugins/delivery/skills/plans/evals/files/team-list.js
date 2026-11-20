export function activeTeamQuery(filters) {
  return new URLSearchParams(filters).toString();
}

export function teamListPath(workspaceId, query) {
  return `/api/workspaces/${workspaceId}/teams?${query}`;
}
