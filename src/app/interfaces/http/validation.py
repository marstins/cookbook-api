from flask import jsonify
from pydantic import ValidationError

FIELD_LABELS = {
    "title": "Título",
    "description": "Descrição",
    "instructions": "Modo de preparo",
    "ingredients": "Ingredientes",
    "is_public": "Receita pública",
    "recipe_id": "Receita",
    "source_data": "Arquivo",
    "name": "Nome",
    "new_name": "Novo nome",
    "email": "E-mail",
    "password": "Senha",
    "old_password": "Senha atual",
    "new_password": "Nova senha",
    "page": "Página",
    "per_page": "Itens por página",
}

TYPE_ERRORS = {
    "string_type": "deve ser um texto",
    "bool_type": "deve ser verdadeiro ou falso",
    "bool_parsing": "deve ser verdadeiro ou falso",
    "int_type": "deve ser um número inteiro",
    "int_parsing": "deve ser um número inteiro",
    "list_type": "deve ser uma lista",
    "dict_type": "formato inválido",
    "model_type": "formato inválido",
}


def _field_label(loc: tuple) -> str:
    if len(loc) >= 2 and loc[0] == "ingredients" and isinstance(loc[1], int):
        return f"Ingrediente {loc[1] + 1}"
    for part in reversed(loc):
        if isinstance(part, str):
            return FIELD_LABELS.get(part, part)
    return "Requisição"


def _describe(error: dict) -> str:
    kind = error["type"]
    ctx = error.get("ctx") or {}

    if kind == "missing":
        return "obrigatório"
    if kind == "string_too_short":
        minimum = ctx.get("min_length", 1)
        if minimum <= 1:
            return "obrigatório"
        return f"mínimo de {minimum} caracteres"
    if kind == "string_too_long":
        return f"máximo de {ctx.get('max_length')} caracteres"
    if kind == "too_short":
        minimum = ctx.get("min_length", 1)
        noun = "ingrediente" if error["loc"] and error["loc"][-1] == "ingredients" else "item"
        return f"adicione ao menos {minimum} {noun}" + ("" if minimum == 1 else "s")
    if kind == "too_long":
        return f"no máximo {ctx.get('max_length')} itens"
    if kind == "string_pattern_mismatch":
        if error["loc"] and error["loc"][-1] == "source_data":
            return "envie um arquivo PNG, JPG ou PDF"
        return "formato inválido"
    if kind == "value_error" and "email" in error.get("msg", "").lower():
        return "e-mail inválido"
    if kind == "greater_than_equal":
        return f"deve ser no mínimo {ctx.get('ge')}"
    if kind == "greater_than":
        return f"deve ser maior que {ctx.get('gt')}"
    if kind == "less_than_equal":
        return f"deve ser no máximo {ctx.get('le')}"
    if kind == "less_than":
        return f"deve ser menor que {ctx.get('lt')}"
    return TYPE_ERRORS.get(kind, "valor inválido")


def translate_errors(exc: ValidationError) -> list[dict]:
    translated = []
    for error in exc.errors():
        loc = tuple(error.get("loc", ()))
        translated.append({
            "field": ".".join(str(part) for part in loc),
            "message": f"{_field_label(loc)}: {_describe(error)}.",
        })
    return translated


def validation_error_response(exc: ValidationError):
    errors = translate_errors(exc)
    return (
        jsonify(
            {
                "error": "validation_error",
                "message": " ".join(error["message"] for error in errors),
                "code": "VALIDATION_ERROR",
                "errors": errors,
            }
        ),
        422,
    )
