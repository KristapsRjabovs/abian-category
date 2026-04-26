import { getSql, loadState, loadTreeNodes, loadMappings,
         loadSupplierCategories, buildPaths, csvRow } from "./_db.mjs";

export default async (req) => {
  const url      = new URL(req.url);
  const supplier = url.searchParams.get("supplier") || "also_data";

  const sql      = getSql();
  const state    = await loadState(sql);
  const nodes    = await loadTreeNodes(sql);
  const all_sc   = await loadSupplierCategories(sql);
  const mappings = await loadMappings(sql);

  const deleted   = new Set(state.deleted);
  const paths     = buildPaths(nodes, deleted);
  const liveCodes = new Set(nodes.filter(n => !deleted.has(n.code)).map(n => n.code));

  const byCat = new Map();
  for (const m of mappings) {
    if (m.supplier !== supplier) continue;
    if (!liveCodes.has(m.tree_code)) continue;
    (byCat.get(m.category) || byCat.set(m.category, []).get(m.category)).push(m.tree_code);
  }

  const lines = [csvRow(["supplier_name", "supplier_category",
                         "client_category_code", "client_category_label"])];
  for (const r of all_sc.filter(r => r.supplier === supplier)) {
    const codes = byCat.get(r.category) || [];
    if (!codes.length) {
      lines.push(csvRow([supplier, r.category, "", ""]));
    } else {
      for (const code of codes) {
        lines.push(csvRow([supplier, r.category, code, paths[code] || ""]));
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
