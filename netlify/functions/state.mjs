import { getSql, loadState, loadTreeNodes, loadMappings,
         loadSupplierCategories, loadSeoMap, buildSupmap } from "./_db.mjs";

export default async () => {
  const sql   = getSql();
  const state = await loadState(sql);
  const nodes = await loadTreeNodes(sql);
  const sc    = await loadSupplierCategories(sql);
  const ms    = await loadMappings(sql);
  const seo   = await loadSeoMap(sql);

  const deleted   = new Set(state.deleted);
  const liveCodes = new Set(nodes.filter(n => !deleted.has(n.code)).map(n => n.code));
  const supmap    = buildSupmap(sc, ms, deleted, liveCodes);
  // Backfill empty entries for every supplier category so the editor knows
  // about unmapped ones.
  for (const r of sc) {
    const k = r.supplier + "||" + r.category;
    if (!(k in supmap)) supmap[k] = [];
  }

  return Response.json({
    supmap,
    deleted:           state.deleted,
    confirmed:         state.confirmed,
    content_confirmed: state.content_confirmed,
    order:             state.order,
    renames:           {},  // applied to tree_nodes.label on save; no need to surface
    seo,
    tree_nodes: nodes.map(n => ({ code: n.code, label: n.label, parent_code: n.parent_code })),
  });
};

export const config = { path: "/api/state" };
