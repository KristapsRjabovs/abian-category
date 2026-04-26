import { getStore } from "@netlify/blobs";

// Snapshot the live Blobs state in the exact shape state.json expects.
// Hit the URL, copy the JSON, paste into state.json in git, push.
// This is the supported way to keep the committed snapshot in sync with
// what the user has actually saved in the hosted UI.
//
//   curl https://<site>/api/sync-state-json > state.json

export default async () => {
  try {
    const store = getStore("category-state");
    const state = (await store.get("state", { type: "json" })) || {};

    // Derive overrides (category -> [codes]) for legacy build.py compatibility.
    const overrides = {};
    for (const [key, codes] of Object.entries(state.supmap || {})) {
      const sep = key.indexOf("||");
      if (sep < 0) continue;
      const cat = key.slice(sep + 2);
      const seen = new Set(overrides[cat] || []);
      for (const c of codes || []) seen.add(c);
      if (seen.size) overrides[cat] = [...seen];
    }

    const out = {
      deleted:           [...(state.deleted   || [])].sort(),
      confirmed:         [...(state.confirmed || [])].sort(),
      content_confirmed: [...(state.content_confirmed || [])].sort(),
      order:             state.order   || {},
      renames:           state.renames || {},
      tree_nodes:        state.tree_nodes || [],
      supmap:            state.supmap     || {},
      overrides,
    };

    return new Response(JSON.stringify(out, null, 2), {
      headers: { "Content-Type": "application/json; charset=utf-8" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500, headers: { "Content-Type": "application/json" },
    });
  }
};

export const config = { path: "/api/sync-state-json" };
