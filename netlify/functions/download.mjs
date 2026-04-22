import { getStore } from "@netlify/blobs";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const appData = JSON.parse(readFileSync(join(__dirname, "_data.json"), "utf-8"));

function csvRow(values) {
  return values.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(",");
}

export default async (req, context) => {
  const url      = new URL(req.url);
  const supplier = url.searchParams.get("supplier") || "also_data";

  let state = {};
  try {
    const store = getStore("category-state");
    state = (await store.get("state", { type: "json" })) || {};
  } catch {}

  const supmap     = state.supmap || {};
  const { paths, sources } = appData;
  const categories = sources[supplier] || [];

  const lines = [csvRow(["supplier_name", "supplier_category", "client_category_code", "client_category_label"])];
  for (const [sup, cat] of categories) {
    const codes = supmap[sup + "||" + cat] || [];
    if (codes.length === 0) {
      lines.push(csvRow([sup, cat, "", ""]));
    } else {
      for (const code of codes) {
        lines.push(csvRow([sup, cat, code, paths[code] || ""]));
      }
    }
  }

  const filename = supplier === "also_data" ? "also_mapping.csv" : "elko_mapping.csv";
  return new Response(lines.join("\r\n") + "\r\n", {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  });
};

export const config = { path: "/api/download" };
