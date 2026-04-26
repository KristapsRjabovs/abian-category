import { getStore } from "@netlify/blobs";

// One-shot admin endpoint: wipes the stored SEO delta in Netlify Blobs so the
// merge in state.mjs falls through to the baked content from the latest build.
// Safe to run any time; only the SEO portion of state is cleared, mappings and
// tree structure are untouched.
//
// Usage:
//   curl https://<site>/api/reset-seo?confirm=yes

export default async (req) => {
  const url = new URL(req.url);
  if (url.searchParams.get("confirm") !== "yes") {
    return new Response(
      "Append ?confirm=yes to actually clear the SEO delta in Blobs.\n",
      { status: 400, headers: { "Content-Type": "text/plain" } }
    );
  }
  try {
    const store = getStore("category-state");
    const state = (await store.get("state", { type: "json" })) || {};
    const before = state.seo ? Object.keys(state.seo).length : 0;
    delete state.seo;
    await store.setJSON("state", state);
    return Response.json({ ok: true, cleared_entries: before });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

export const config = { path: "/api/reset-seo" };
