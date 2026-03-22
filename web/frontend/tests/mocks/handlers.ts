import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("http://localhost/api/csrf-token", () =>
    HttpResponse.json({
      success: true,
      data: { csrf_token: "msw-default-csrf" },
    }),
  ),
];
