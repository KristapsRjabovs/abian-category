import { getStore } from "@netlify/blobs";
import { readFileSync } from "fs";

const appData = JSON.parse(readFileSync(new URL("./_data.json", import.meta.url), "utf-8"));

function csvRow(values) {
  return values.map(v => '"' + String(v ?? "").replace(/"/g, '""') + '"').join(",");
}

function wordCount(text) {
  return ((text || "").trim().match(/\S+/g) || []).length;
}

function trigrams(text) {
  const t = (text || "").toLowerCase().replace(/\s+/g, " ").trim();
  if (t.length < 3) return new Set([t]);
  const out = new Set();
  for (let i = 0; i <= t.length - 3; i++) out.add(t.slice(i, i + 3));
  return out;
}

function similarity(a, b) {
  const ga = trigrams(a), gb = trigrams(b);
  if (!ga.size || !gb.size) return 0;
  let inter = 0;
  for (const x of ga) if (gb.has(x)) inter++;
  const union = ga.size + gb.size - inter;
  return union ? inter / union : 0;
}

// Stable category IDs — pre-order traversal of the live tree.
function buildCategoryIds(treeNodes, deleted, order) {
  const byParent = new Map();
  for (const n of treeNodes) {
    if (deleted.has(n.code)) continue;
    const p = n.parent_code || null;
    if (!byParent.has(p)) byParent.set(p, []);
    byParent.get(p).push(n);
  }
  const sortChildren = (parentCode) => {
    const lst = byParent.get(parentCode) || [];
    const key = parentCode === null ? "__root__" : parentCode;
    const saved = (order && order[key]) || [];
    if (saved.length) {
      const pos = new Map(saved.map((c, i) => [c, i]));
      lst.sort((a, b) => {
        const pa = pos.has(a.code) ? [0, pos.get(a.code)] : [1, a.label.toLowerCase()];
        const pb = pos.has(b.code) ? [0, pos.get(b.code)] : [1, b.label.toLowerCase()];
        return pa[0] - pb[0] || (pa[1] > pb[1] ? 1 : pa[1] < pb[1] ? -1 : 0);
      });
    } else {
      lst.sort((a, b) => {
        const ao = a.code.endsWith("/other") || a.label.toLowerCase().startsWith("other") ? 1 : 0;
        const bo = b.code.endsWith("/other") || b.label.toLowerCase().startsWith("other") ? 1 : 0;
        return ao - bo || a.label.localeCompare(b.label);
      });
    }
    return lst;
  };
  const ids = new Map();
  let counter = 1;
  const walk = (parent) => {
    for (const n of sortChildren(parent)) {
      ids.set(n.code, counter++);
      walk(n.code);
    }
  };
  walk(null);
  return ids;
}

export default async (req) => {
  const url = new URL(req.url);
  const force = url.searchParams.get("force") === "true";

  let state = {};
  try {
    const store = getStore("category-state");
    state = (await store.get("state", { type: "json" })) || {};
  } catch {}

  // Tree nodes: prefer Blobs state (live edits), else build from baked paths.
  let treeNodes = state.tree_nodes;
  if (!Array.isArray(treeNodes) || !treeNodes.length) {
    // Reconstruct minimal node list from baked paths — every code with a parent path segment.
    const codes = Object.keys(appData.paths || {});
    treeNodes = codes.map(code => {
      const parts = code.split("/");
      const parent_code = parts.length > 1 ? parts.slice(0, -1).join("/") : null;
      // Use last path segment of breadcrumb for label fallback
      const path = appData.paths[code] || "";
      const label = path.split(" > ").pop() || code;
      return { code, label, parent_code };
    });
  }

  const deleted = new Set(state.deleted || []);
  const order = state.order || {};
  const cat_ids = buildCategoryIds(treeNodes, deleted, order);

  // Merge SEO: Blobs edits override baked content per-field
  const bakedSeo = appData.seo || {};
  const blobsSeo = state.seo || {};
  const seoFor = (code) => ({ ...(bakedSeo[code] || {}), ...(blobsSeo[code] || {}) });

  // Validation
  const REQUIRED = ["name_lv", "name_en", "slug_lv", "slug_en", "seo_desc_lv", "seo_desc_en"];
  const problems = [];
  const liveNodes = treeNodes.filter(n => !deleted.has(n.code));
  for (const n of liveNodes) {
    const s = seoFor(n.code);
    for (const f of REQUIRED) {
      if (!(s[f] || "").trim()) problems.push({ code: n.code, field: f, reason: "missing" });
    }
    for (const lang of ["en", "lv"]) {
      const w = wordCount(s["seo_desc_" + lang]);
      if (w && (w < 50 || w > 70)) {
        problems.push({ code: n.code, field: "seo_desc_" + lang,
                        reason: w < 50 ? `too short (${w} words, min 50)` : `too long (${w} words, max 70)` });
      }
    }
  }
  // Cannibalization
  for (const lang of ["en", "lv"]) {
    const items = liveNodes.map(n => [n.code, seoFor(n.code)["seo_desc_" + lang] || ""]).filter(([_, d]) => d);
    for (let i = 0; i < items.length; i++) {
      for (let j = i + 1; j < items.length; j++) {
        const sc = similarity(items[i][1], items[j][1]);
        if (sc >= 0.75) {
          problems.push({ code: items[i][0], field: "seo_desc_" + lang,
                          reason: `cannibalization with ${items[j][0]} (similarity ${sc.toFixed(3)})` });
        }
      }
    }
  }

  if (problems.length && !force) {
    return new Response(JSON.stringify({ ok: false, total: problems.length,
                                          problems: problems.slice(0, 200) }),
                        { status: 422, headers: { "Content-Type": "application/json" } });
  }

  // CSV
  const lines = [csvRow(["category_id", "parent_category_id", "category_path",
                         "category_name_lv", "category_name_en",
                         "url_slug_lv", "url_slug_en",
                         "seo_description_lv", "seo_description_en"])];
  const sorted = [...liveNodes].sort((a, b) => cat_ids.get(a.code) - cat_ids.get(b.code));
  for (const n of sorted) {
    const s = seoFor(n.code);
    const parent_id = n.parent_code ? (cat_ids.get(n.parent_code) || 0) : 0;
    lines.push(csvRow([
      cat_ids.get(n.code), parent_id, appData.paths[n.code] || "",
      s.name_lv || "", s.name_en || "",
      s.slug_lv || "", s.slug_en || "",
      s.seo_desc_lv || "", s.seo_desc_en || "",
    ]));
  }

  return new Response(lines.join("\r\n") + "\r\n", {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="magento_categories.csv"',
    },
  });
};

export const config = { path: "/api/category-export" };
