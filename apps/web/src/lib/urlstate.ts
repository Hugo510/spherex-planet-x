import { createParser, parseAsBoolean, parseAsFloat, parseAsInteger, parseAsString, parseAsStringLiteral } from "nuqs";

/** `?embed=1` (o true) → sin cromo. */
export const parseAsFlag = createParser({
  parse: (v) => v === "1" || v === "true",
  serialize: (v) => (v ? "1" : "0"),
});

/** Estado completo del visor en la URL: ?field&ra&dec&epoch&pmra&pmdec&fov&det&visit&frame&mode&stretch&clip&cmap&embed&a&b */
export const viewerParsers = {
  field: parseAsString.withDefault(""), // vacío + ra/dec = modo en vivo; vacío sin ra/dec = showcase wise0855
  ra: parseAsFloat,
  dec: parseAsFloat,
  epoch: parseAsFloat.withDefault(2016),
  pmra: parseAsFloat.withDefault(0),
  pmdec: parseAsFloat.withDefault(0),
  fov: parseAsFloat.withDefault(0.1),
  det: parseAsString.withDefault(""),
  visit: parseAsInteger.withDefault(0),
  frame: parseAsInteger.withDefault(-1), // −1 = coadd de la visita; ≥ 0 = exposición (escalera de λ)
  mode: parseAsStringLiteral(["blink", "diff", "trail"] as const).withDefault("blink"),
  stretch: parseAsFloat.withDefault(3), // parámetro a del asinh
  clip: parseAsString.withDefault("5,99.7"),
  cmap: parseAsStringLiteral(["gray", "cividis"] as const).withDefault("gray"),
  invert: parseAsBoolean.withDefault(false),
  embed: parseAsFlag.withDefault(false),
  a: parseAsString.withDefault(""),
  b: parseAsString.withDefault(""),
  speed: parseAsFloat.withDefault(1.5), // cuadros por segundo
  play: parseAsBoolean.withDefault(false),
  panel: parseAsStringLiteral(["none", "known", "spectrum", "aladin", "class", "changes"] as const).withDefault("none"),
  pick: parseAsString.withDefault(""), // "x,y" clic en el visor
};
