import { getStore } from "@netlify/blobs";

export default async (req) => {
  try {
    const payload = await req.json();
    const store = getStore("category-state");
    const existing = (await store.get("state", { type: "json" })) || {};

    // SEO is special: Blobs should only ever hold the user's accumulated
    // edits (delta vs baked). Apply incoming seo_edits on top of existing
    // delta; never blindly replace with the full SEO map echoed by the UI.
    const existingSeo = (existing.seo && typeof existing.seo === "object") ? existing.seo : {};
    const seoEdits = (payload.seo_edits && typeof payload.seo_edits === "object")
      ? payload.seo_edits : {};
    const mergedSeo = { ...existingSeo };
    for (const [code, fields] of Object.entries(seoEdits)) {
      const cur = { ...(mergedSeo[code] || {}) };
      for (const [k, v] of Object.entries(fields || {})) {
        if (typeof v === "string" && v.trim()) cur[k] = v;
      }
      if (Object.keys(cur).length) mergedSeo[code] = cur;
    }

    const next = {
      ...payload,
      seo: mergedSeo,
    };
    delete next.seo_edits; // not part of stored state
    await store.setJSON("state", next);

    return Response.json({
      ok: true,
      confirmed: (payload.confirmed || []).length,
      deleted:   (payload.deleted   || []).length,
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

export const config = { path: "/api/save", method: "POST" };
