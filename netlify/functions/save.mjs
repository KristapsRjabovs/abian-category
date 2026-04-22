import { getStore } from "@netlify/blobs";

export default async (req, context) => {
  try {
    const payload = await req.json();
    const store = getStore("category-state");
    await store.setJSON("state", payload);
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
