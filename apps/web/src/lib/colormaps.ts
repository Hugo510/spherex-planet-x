/** Cividis (Nuñez, Anderton & Renslow 2018), 32 nodos RGB interpolados linealmente; gris; ambos invertibles. */
const CIVIDIS_NODES: [number, number, number][] = [
  [0, 32, 77], [0, 37, 84], [0, 42, 92], [0, 48, 100], [0, 53, 108], [11, 58, 110], [28, 63, 110], [39, 68, 110],
  [48, 74, 110], [56, 79, 111], [64, 84, 112], [71, 89, 113], [78, 95, 114], [84, 100, 116], [91, 105, 118], [97, 111, 120],
  [104, 116, 122], [110, 122, 124], [117, 128, 125], [124, 134, 126], [131, 139, 126], [139, 145, 125], [147, 151, 124],
  [155, 157, 122], [163, 163, 119], [172, 169, 115], [181, 176, 111], [191, 182, 106], [201, 188, 100], [211, 195, 92],
  [222, 202, 83], [234, 209, 72],
];

export type Cmap = "gray" | "cividis";

export function buildLut(cmap: Cmap, invert: boolean): Uint8ClampedArray {
  const lut = new Uint8ClampedArray(256 * 3);
  for (let i = 0; i < 256; i++) {
    const t = (invert ? 255 - i : i) / 255;
    let r: number, g: number, b: number;
    if (cmap === "gray") {
      r = g = b = t * 255;
    } else {
      const x = t * (CIVIDIS_NODES.length - 1);
      const j = Math.min(Math.floor(x), CIVIDIS_NODES.length - 2);
      const f = x - j;
      const a = CIVIDIS_NODES[j], c = CIVIDIS_NODES[j + 1];
      r = a[0] + (c[0] - a[0]) * f; g = a[1] + (c[1] - a[1]) * f; b = a[2] + (c[2] - a[2]) * f;
    }
    lut[i * 3] = r; lut[i * 3 + 1] = g; lut[i * 3 + 2] = b;
  }
  return lut;
}
