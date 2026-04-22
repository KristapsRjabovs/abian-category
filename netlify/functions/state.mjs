import { getStore } from "@netlify/blobs";

export default async (req, context) => {
  try {
    const store = getStore("category-state");
    const state = await store.get("state", { type: "json" });
    return Response.json(state || {});
  } catch (e) {
    return Response.json({});
  }
};

export const config = { path: "/api/state" };
