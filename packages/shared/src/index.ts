// Tipos compartidos entre apps/web y el contrato OpenAPI de apps/api.
// `api.d.ts` se genera con `pnpm gen:types` a partir de apps/api/openapi.json (F2).
export type { components, paths } from "./api";
export * from "./constants";
