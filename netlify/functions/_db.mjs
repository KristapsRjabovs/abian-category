import { neon } from "@netlify/neon";

// One Neon SQL tag per cold start.
//   const sql = getSql();
//   const rows = await sql`SELECT * FROM tree_nodes`;
let _sql;
export function getSql() {
  if (!_sql) _sql = neon();
  return _sql;
}

// ── reads ──────────────────────────────────────────────────────────────────

export async function loadState(sql) {
  const rows = await sql`SELECT key, value FROM tree_state`;
  const out = {};
  for (const r of rows) {
    try { out[r.key] = JSON.parse(r.value); } catch { out[r.key] = r.value; }
  }
  return {
    deleted:           out.deleted           || [],
    confirmed:         out.confirmed         || [],
    content_confirmed: out.content_confirmed || [],
    order:             out.order             || {},
  };
}

export async function loadTreeNodes(sql) {
  return await sql`SELECT code, label, parent_code, name_lv, slug_lv, slug_en,
                          seo_desc_lv, seo_desc_en, meta_desc_lv, meta_desc_en,
                          bottom_seo_lv, bottom_seo_en
                   FROM tree_nodes ORDER BY code`;
}

export async function loadMappings(sql) {
  return await sql`SELECT supplier, category, tree_code FROM mappings`;
}

export async function loadSupplierCategories(sql) {
  return await sql`SELECT supplier, category FROM supplier_categories
                   ORDER BY supplier, id`;
}

export async function loadSeoMap(sql) {
  const rows = await loadTreeNodes(sql);
  const out = {};
  for (const r of rows) {
    out[r.code] = {
      name_en:       r.label          || "",
      name_lv:       r.name_lv        || "",
      slug_lv:       r.slug_lv        || "",
      slug_en:       r.slug_en        || "",
      seo_desc_lv:   r.seo_desc_lv    || "",
      seo_desc_en:   r.seo_desc_en    || "",
      meta_desc_lv:  r.meta_desc_lv   || "",
      meta_desc_en:  r.meta_desc_en   || "",
      bottom_seo_lv: r.bottom_seo_lv  || "",
      bottom_seo_en: r.bottom_seo_en  || "",
    };
  }
  return out;
}

// ── builders the editor used to read out of _data.json ─────────────────────

export function buildSupmap(supplierCats, mappings, deleted, liveCodes) {
  const byCat = new Map();
  for (const m of mappings) {
    if (!liveCodes.has(m.tree_code)) continue;
    if (deleted.has(m.tree_code))    continue;
    const k = m.supplier + "||" + m.category;
    (byCat.get(k) || byCat.set(k, []).get(k)).push(m.tree_code);
  }
  const supmap = {};
  for (const r of supplierCats) {
    const k = r.supplier + "||" + r.category;
    supmap[k] = byCat.get(k) || [];
  }
  return supmap;
}

export function buildPaths(nodes, deleted) {
  const label = new Map(); const parent = new Map();
  for (const n of nodes) {
    if (deleted.has(n.code)) continue;
    label.set(n.code, n.label);
    parent.set(n.code, n.parent_code);
  }
  const paths = {};
  for (const code of label.keys()) {
    const parts = []; let cur = code;
    while (cur) { parts.push(label.get(cur) || cur); cur = parent.get(cur); }
    paths[code] = parts.reverse().join(" > ");
  }
  return paths;
}

// ── CSV helper used by both download endpoints ─────────────────────────────

export function csvRow(values) {
  return values.map(v => '"' + String(v ?? "").replace(/"/g, '""') + '"').join(",");
}
