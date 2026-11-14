import fs from "node:fs";
import path from "node:path";
import type { ShowcaseIndex } from "./types";

/** Índice del showcase leído en build (sitio estático): apps/web/public/showcase/index.json. */
export function readShowcaseIndex(): ShowcaseIndex {
  const p = path.join(process.cwd(), "public", "showcase", "index.json");
  if (!fs.existsSync(p)) return { generated_at: "", attribution: "", fields: [] };
  return JSON.parse(fs.readFileSync(p, "utf8")) as ShowcaseIndex;
}
