import { getSql } from "./_db.mjs";

// Standalone notes save. One node, one column, no save-guard noise.
export default async (req) => {
  try {
    const { code, notes } = await req.json();
    if (!code) {
      return new Response(JSON.stringify({ ok: false, error: "code is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } });
    }
    const sql = getSql();
    await sql`UPDATE tree_nodes SET notes = ${notes ?? ""} WHERE code = ${code}`;
    return Response.json({ ok: true });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: e.message, stack: e.stack }),
      { status: 500, headers: { "Content-Type": "application/json" } });
  }
};

export const config = { path: "/api/save-notes", method: "POST" };
