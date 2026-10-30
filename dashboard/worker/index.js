
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


if (url.pathname === "/api/searches" &&
    request.method === "POST") {
  try {
    const body = await request.json();

    const keyword = String(body.keyword || "").trim();
    const maxPrice = Number(body.max_price);

    if (
      !keyword ||
      keyword.length > 100 ||
      body.max_price === "" ||
      body.max_price == null ||
      !Number.isFinite(maxPrice) ||
      maxPrice <= 0
    ) {
      return Response.json(
        { error: "Invalid keyword or price" },
        { status: 400 }
      );
    }

    const id = crypto.randomUUID();

    await env.DB.prepare(
      `INSERT INTO searches
       (id, keyword, max_price, active)
       VALUES (?, ?, ?, 1)`
    ).bind(id, keyword, maxPrice).run();

    return Response.json({
      id,
      keyword,
      max_price: maxPrice,
      active: 1
    }, { status: 201 });

  } catch (error) {
    console.error("Failed to create search", error);
    return Response.json(
      { error: "Unable to create search" },
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
