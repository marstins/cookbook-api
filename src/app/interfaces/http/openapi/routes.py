"""Cookbook API: registro das rotas de documentação (spec + Swagger UI)."""

from flask import Flask, Response, jsonify, render_template_string

from .spec import build_openapi_spec

_SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Cookbook API — Documentação</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" crossorigin="anonymous" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin="anonymous"></script>
  <script>
    window.onload = function () {
      window.ui = SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
      });
    };
  </script>
</body>
</html>"""


def register_openapi_routes(app: Flask) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(build_openapi_spec())

    @app.get("/docs")
    def swagger_ui():
        return Response(
            render_template_string(_SWAGGER_UI_HTML),
            mimetype="text/html; charset=utf-8",
        )
