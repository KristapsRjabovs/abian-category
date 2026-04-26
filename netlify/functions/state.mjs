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
      // name_en is mirrored from the tree label and is not user-editable
      // through SEO. Skip it from Blobs so it can't drift from the label.
      if (k === "name_en") continue;
      if (typeof v === "string" && v.trim()) out[k] = v;
    }
    merged[code] = out;
  }
  // Force name_en from live tree labels (Blobs first, baked paths fallback).
  const liveNodes = Array.isArray(state.tree_nodes) ? state.tree_nodes : [];
  if (liveNodes.length) {
    for (const n of liveNodes) {
      merged[n.code] = merged[n.code] || {};
      merged[n.code].name_en = n.label;
    }
  }
  state.seo = merged;
  return Response.json(state);
};

export const config = { path: "/api/state" };
