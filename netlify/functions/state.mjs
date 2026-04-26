import { getStore } from "@netlify/blobs";
import { readFileSync } from "fs";

const appData = JSON.parse(readFileSync(new URL("./_data.json", import.meta.url), "utf-8"));

export default async (req, context) => {
  let state = {};
  try {
    const store = getStore("category-state");
    state = (await store.get("state", { type: "json" })) || {};
  } catch {}

  // Merge SEO: baked content from build is the floor; only non-empty Blobs
  // fields override per-field. Empty strings in Blobs (left over from earlier
  // saves before this content was authored) MUST NOT overwrite a baked value.
  const bakedSeo = appData.seo || {};
  const blobSeo  = state.seo  || {};
  const merged = {};
  for (const code of new Set([...Object.keys(bakedSeo), ...Object.keys(blobSeo)])) {
    const out = { ...(bakedSeo[code] || {}) };
    for (const [k, v] of Object.entries(blobSeo[code] || {})) {
      if (typeof v === "string" && v.trim()) out[k] = v;
    }
    merged[code] = out;
  }
  state.seo = merged;
  return Response.json(state);
};

export const config = { path: "/api/state" };
