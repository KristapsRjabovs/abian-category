import { getStore } from "@netlify/blobs";
import { readFileSync } from "fs";

const appData = JSON.parse(readFileSync(new URL("./_data.json", import.meta.url), "utf-8"));

export default async (req, context) => {
  let state = {};
  try {
    const store = getStore("category-state");
    state = (await store.get("state", { type: "json" })) || {};
  } catch {}

  // Merge SEO: baked content from build is the default; per-node Blobs edits override.
  const bakedSeo = appData.seo || {};
  const blobSeo  = state.seo  || {};
  const merged = {};
  for (const code of new Set([...Object.keys(bakedSeo), ...Object.keys(blobSeo)])) {
    merged[code] = { ...(bakedSeo[code] || {}), ...(blobSeo[code] || {}) };
  }
  state.seo = merged;
  return Response.json(state);
};

export const config = { path: "/api/state" };
