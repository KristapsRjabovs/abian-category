import { getSql, loadState } from "./_db.mjs";

// Builds the breadcrumb path for one node by walking parent_code links.
function buildPath(byCode, code) {
  const parts = [];
  let cur = code;
  while (cur && byCode.has(cur)) {
    parts.unshift(byCode.get(cur).label);
    cur = byCode.get(cur).parent_code;
  }
  return parts.join(" > ");
}

export default async () => {
  try {
    const sql = getSql();
    const nodes = await sql`SELECT code, label, parent_code, notes
                              FROM tree_nodes ORDER BY code`;
    const state = await loadState(sql);
    const deleted          = new Set(state.deleted          || []);
    const confirmed        = new Set(state.confirmed        || []);
    const contentConfirmed = new Set(state.content_confirmed || []);

    const byCode = new Map(nodes.map(n => [n.code, n]));
    const entries = [];
    for (const n of nodes) {
      if (deleted.has(n.code)) continue;
      const notes = (n.notes || "").trim();
      if (!notes) continue;
      entries.push({
        code:  n.code,
        label: n.label,
        path:  buildPath(byCode, n.code),
        notes,
        mappings_confirmed: confirmed.has(n.code),
        content_confirmed:  contentConfirmed.has(n.code),
      });
    }

    let body;
    if (!entries.length) {
      body = "# Category content review notes\n\n" +
             "_No editor notes recorded. Add notes from the SEO panel on " +
             "any tree node to surface them here._\n";
    } else {
      const lines = [
        "# Category content review notes",
        "",
        `You are reviewing SEO content on ${entries.length} category page(s).`,
        "Each block below contains the page identifier, the current " +
        "approval status, and the editor's notes. Update the SEO " +
        "description, meta description and bottom SEO text on each " +
        "page to address every point in the notes. Keep all existing " +
        "constraints (50-70 word seo_desc, 120-160 char meta_desc, " +
        "no brand names, no em-dashes, abbreviations expanded on " +
        "first use, language-mixed where appropriate).",
        "",
      ];
      for (const e of entries) {
        lines.push(`## ${e.label}`);
        lines.push(`- **Path:** ${e.path}`);
        lines.push(`- **Code:** \`${e.code}\``);
        lines.push(`- **Mappings confirmed:** ${e.mappings_confirmed ? "yes" : "no"}`);
        lines.push(`- **Content confirmed:** ${e.content_confirmed ? "yes" : "no"}`);
        lines.push("");
        lines.push("**Notes:**");
        for (const raw of e.notes.split("\n")) {
          const stripped = raw.trim();
          lines.push(stripped ? `> ${stripped}` : ">");
        }
        lines.push("");
        lines.push("---");
        lines.push("");
      }
      body = lines.join("\n").replace(/\s+$/, "") + "\n";
    }

    return new Response(body, {
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Content-Disposition": 'attachment; filename="category-notes.md"',
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message, stack: e.stack }),
      { status: 500, headers: { "Content-Type": "application/json" } });
  }
};

export const config = { path: "/api/notes-export" };
