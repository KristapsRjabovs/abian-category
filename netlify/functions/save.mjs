import { getSql } from "./_db.mjs";

const SEO_COLS = [
  "name_lv", "slug_lv", "slug_en",
  "seo_desc_lv", "seo_desc_en", "meta_desc_lv", "meta_desc_en",
];

export default async (req) => {
  try {
    const payload = await req.json();
    const sql = getSql();

    const treeNodes        = payload.tree_nodes        || [];
    const supmap           = payload.supmap            || {};
    const deleted          = payload.deleted           || [];
    const confirmed        = payload.confirmed         || [];
    const contentConfirmed = payload.content_confirmed || [];
    const order            = payload.order             || {};
    const renames          = payload.renames           || {};
    const seoEdits         = payload.seo_edits         || {};
    const deletedSet       = new Set(deleted);

    // Build the full statement list, then ship it as one transaction so the
    // DB never observes a half-applied save.
    const queries = [];

    // ── tree_nodes sync ───────────────────────────────────────────────
    const existing = new Set(
      (await sql`SELECT code FROM tree_nodes`).map(r => r.code));
    const live = new Set(treeNodes.map(n => n.code));

    // Bulk-upsert via a single VALUES list
    if (treeNodes.length) {
      // Neon serverless tag doesn't accept array-of-tuples directly, so build
      // a parameterised statement: VALUES ($1,$2,$3),($4,$5,$6),...
      const vals = [];
      for (const n of treeNodes) vals.push(n.code, n.label, n.parent_code || null);
      const tuples = treeNodes.map((_, i) =>
        `($${i*3+1}, $${i*3+2}, $${i*3+3})`).join(",");
      queries.push(sql.unsafe(
        `INSERT INTO tree_nodes(code, label, parent_code) VALUES ${tuples}
         ON CONFLICT (code) DO UPDATE
         SET label = EXCLUDED.label, parent_code = EXCLUDED.parent_code`,
        vals));
    }
    // Drop zombies (in DB, not in payload, not intentionally deleted)
    const zombies = [...existing].filter(c => !live.has(c) && !deletedSet.has(c));
    if (zombies.length) {
      queries.push(sql`DELETE FROM tree_nodes WHERE code = ANY(${zombies})`);
    }

    // ── label renames ─────────────────────────────────────────────────
    for (const [code, label] of Object.entries(renames)) {
      queries.push(sql`UPDATE tree_nodes SET label = ${label} WHERE code = ${code}`);
    }

    // ── mappings: drop orphans, replace ───────────────────────────────
    // We can't easily verify orphan codes against post-tx state, so trust the
    // tree_nodes upsert above and accept anything in `live` plus pre-existing.
    const validCodes = new Set([...live, ...existing]);
    let orphansDropped = 0;
    const mapRows = [];
    for (const [key, codes] of Object.entries(supmap)) {
      const sep = key.indexOf("||");
      if (sep < 0) continue;
      const supplier = key.slice(0, sep), category = key.slice(sep + 2);
      for (const code of codes || []) {
        if (validCodes.has(code) && !deletedSet.has(code)) {
          mapRows.push(supplier, category, code);
        } else {
          orphansDropped++;
        }
      }
    }
    queries.push(sql`DELETE FROM mappings`);
    if (mapRows.length) {
      const tuples = [];
      for (let i = 0; i < mapRows.length; i += 3) {
        tuples.push(`($${i+1}, $${i+2}, $${i+3})`);
      }
      queries.push(sql.unsafe(
        `INSERT INTO mappings(supplier, category, tree_code) VALUES ${tuples.join(",")}
         ON CONFLICT DO NOTHING`,
        mapRows));
    }

    // ── SEO edits (whitelist column names) ────────────────────────────
    for (const [code, fields] of Object.entries(seoEdits)) {
      for (const k of SEO_COLS) {
        if (!(k in (fields || {}))) continue;
        const v = fields[k] ?? "";
        // Column whitelisted via SEO_COLS, value parameterised. Safe.
        queries.push(sql.unsafe(
          `UPDATE tree_nodes SET ${k} = $1 WHERE code = $2`,
          [v, code]));
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
