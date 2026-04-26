import { getSql } from "./_db.mjs";

// Whitelisted SEO column updaters. Column names are fixed inline so there
// is no SQL injection risk; only the value is parameterised.
function seoUpdate(sql, code, field, value) {
  switch (field) {
    case "name_lv":       return sql`UPDATE tree_nodes SET name_lv       = ${value} WHERE code = ${code}`;
    case "slug_lv":       return sql`UPDATE tree_nodes SET slug_lv       = ${value} WHERE code = ${code}`;
    case "slug_en":       return sql`UPDATE tree_nodes SET slug_en       = ${value} WHERE code = ${code}`;
    case "seo_desc_lv":   return sql`UPDATE tree_nodes SET seo_desc_lv   = ${value} WHERE code = ${code}`;
    case "seo_desc_en":   return sql`UPDATE tree_nodes SET seo_desc_en   = ${value} WHERE code = ${code}`;
    case "meta_desc_lv":  return sql`UPDATE tree_nodes SET meta_desc_lv  = ${value} WHERE code = ${code}`;
    case "meta_desc_en":  return sql`UPDATE tree_nodes SET meta_desc_en  = ${value} WHERE code = ${code}`;
    case "bottom_seo_lv": return sql`UPDATE tree_nodes SET bottom_seo_lv = ${value} WHERE code = ${code}`;
    case "bottom_seo_en": return sql`UPDATE tree_nodes SET bottom_seo_en = ${value} WHERE code = ${code}`;
    default: return null;
  }
}

const SEO_FIELDS = [
  "name_lv", "slug_lv", "slug_en",
  "seo_desc_lv", "seo_desc_en", "meta_desc_lv", "meta_desc_en",
  "bottom_seo_lv", "bottom_seo_en",
];

export default async (req) => {
  try {
    const payload = await req.json();
    const sql = getSql();

    const force            = !!payload.force;
    const treeNodes        = payload.tree_nodes        || [];
    const supmap           = payload.supmap            || {};
    const deleted          = payload.deleted           || [];
    const confirmed        = payload.confirmed         || [];
    const contentConfirmed = payload.content_confirmed || [];
    const order            = payload.order             || {};
    const renames          = payload.renames           || {};
    const seoEdits         = payload.seo_edits         || {};
    const deletedSet       = new Set(deleted);

    // Safety net: don't let an empty payload wipe a populated database.
    if (!force) {
      const [{ count: treeCount }] = await sql`SELECT COUNT(*)::int AS count FROM tree_nodes`;
      const [{ count: mapCount }]  = await sql`SELECT COUNT(*)::int AS count FROM mappings`;
      if (treeCount > 0 && treeNodes.length === 0) {
        return new Response(JSON.stringify({
          ok: false, error: "empty tree_nodes would wipe DB",
          hint: "set force=true to override" }),
          { status: 409, headers: { "Content-Type": "application/json" } });
      }
      let incomingPairs = 0;
      for (const v of Object.values(supmap)) incomingPairs += (v || []).length;
      if (mapCount > 0 && incomingPairs === 0) {
        return new Response(JSON.stringify({
          ok: false, error: "empty supmap would wipe mappings",
          hint: "set force=true to override" }),
          { status: 409, headers: { "Content-Type": "application/json" } });
      }
    }

    // Build the transaction queue. Every entry MUST be a query produced
    // by the sql`` template tag — sql.transaction() is strict about that.
    const queries = [];

    // ── tree_nodes upsert ─────────────────────────────────────────────
    const existingRows = await sql`SELECT code FROM tree_nodes`;
    const existing = new Set(existingRows.map(r => r.code));
    const live = new Set(treeNodes.map(n => n.code));
    for (const n of treeNodes) {
      queries.push(sql`
        INSERT INTO tree_nodes(code, label, parent_code)
        VALUES (${n.code}, ${n.label}, ${n.parent_code || null})
        ON CONFLICT (code) DO UPDATE
          SET label = EXCLUDED.label, parent_code = EXCLUDED.parent_code`);
    }
    // Drop zombies (in DB, not in payload, not intentionally deleted)
    for (const code of existing) {
      if (!live.has(code) && !deletedSet.has(code)) {
        queries.push(sql`DELETE FROM tree_nodes WHERE code = ${code}`);
      }
    }

    // ── label renames ─────────────────────────────────────────────────
    for (const [code, label] of Object.entries(renames)) {
      queries.push(sql`UPDATE tree_nodes SET label = ${label} WHERE code = ${code}`);
    }

    // ── mappings: orphan-filter then replace ──────────────────────────
    const validCodes = new Set([...live, ...existing]);
    let orphansDropped = 0;
    const mapRows = [];
    for (const [key, codes] of Object.entries(supmap)) {
      const sep = key.indexOf("||");
      if (sep < 0) continue;
      const supplier = key.slice(0, sep), category = key.slice(sep + 2);
      for (const code of codes || []) {
        if (validCodes.has(code) && !deletedSet.has(code)) {
          mapRows.push([supplier, category, code]);
        } else {
          orphansDropped++;
        }
      }
    }
    queries.push(sql`DELETE FROM mappings`);
    for (const [s, c, t] of mapRows) {
      queries.push(sql`
        INSERT INTO mappings(supplier, category, tree_code)
        VALUES (${s}, ${c}, ${t}) ON CONFLICT DO NOTHING`);
    }

    // ── SEO edits ─────────────────────────────────────────────────────
    for (const [code, fields] of Object.entries(seoEdits)) {
      for (const k of SEO_FIELDS) {
        if (!(k in (fields || {}))) continue;
        const q = seoUpdate(sql, code, k, fields[k] ?? "");
        if (q) queries.push(q);
      }
    }

    // ── tree_state ────────────────────────────────────────────────────
    const upsert = (key, value) => sql`
      INSERT INTO tree_state(key, value) VALUES (${key}, ${JSON.stringify(value)})
      ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`;
    queries.push(upsert("deleted",           [...new Set(deleted)].sort()));
    queries.push(upsert("confirmed",         [...new Set(confirmed)].sort()));
    queries.push(upsert("content_confirmed", [...new Set(contentConfirmed)].sort()));
    queries.push(upsert("order",   order));

    // Single round-trip; atomic on the Neon side.
    await sql.transaction(queries);

    return Response.json({
      ok: true,
      confirmed:         confirmed.length,
      deleted:           deleted.length,
      content_confirmed: contentConfirmed.length,
      seo_updated:       Object.keys(seoEdits).length,
      orphans_dropped:   orphansDropped,
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message, stack: e.stack }),
      { status: 500, headers: { "Content-Type": "application/json" } });
  }
};

export const config = { path: "/api/save", method: "POST" };
