
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/health") {
      try {
        const result = await env.DB
          .prepare("SELECT COUNT(*) AS count FROM searches")
          .first();

        return Response.json({
          status: "ok",
          database: "connected",
          searches: result.count
        });
      } catch (error) {
        console.error("Database health check failed", error);
        return Response.json(
          { error: "Database unavailable" },
          { status: 503 }
        );
      }
    }

    if (url.pathname === "/api/searches" &&
        request.method === "GET") {
      try {
        const { results } = await env.DB.prepare(
          `SELECT id, keyword, max_price, min_price,
                  exclude_keywords, active, created_at
           FROM searches
           ORDER BY created_at DESC`
        ).all();

        return Response.json(results);
      } catch (error) {
        console.error("Failed to load searches", error);
        return Response.json(
          { error: "Unable to load searches" },
          { status: 500 }
        );
      }
    }

    return Response.json(
      { error: "Not found" },
      { status: 404 }
    );
  }
};
