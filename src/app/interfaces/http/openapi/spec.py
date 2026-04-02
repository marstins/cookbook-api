"""Cookbook API — especificação OpenAPI 3.0 gerada em código (sem anotações nos blueprints)."""


def build_openapi_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Cookbook API",
            "version": "1.0.0",
            "description": (
                "Cookbook API: serviço HTTP de usuários, autenticação e receitas "
                "(públicas, privadas e descoberta)."
            ),
        },
        "servers": [{"url": "/", "description": "Mesma origem da aplicação Flask"}],
        "tags": [
            {"name": "Sistema"},
            {"name": "Usuários"},
            {"name": "Autenticação"},
            {"name": "Receitas"},
        ],
        "paths": _paths(),
        "components": {
            "parameters": {
                "UserIdHeader": {
                    "name": "user-id",
                    "in": "header",
                    "required": True,
                    "schema": {"type": "string"},
                },
                "UserIdHeaderOptional": {
                    "name": "user-id",
                    "in": "header",
                    "required": False,
                    "schema": {"type": "string"},
                },
                "PageQuery": {
                    "name": "page",
                    "in": "query",
                    "schema": {"type": "integer", "minimum": 1, "default": 1},
                },
                "PerPageQuery": {
                    "name": "per_page",
                    "in": "query",
                    "schema": {"type": "integer", "minimum": 1, "default": 10},
                },
            },
            "schemas": _schemas(),
        },
    }


def _schemas() -> dict:
    return {
        "UserPublic": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "created_at": {"type": "string", "format": "date-time"},
            },
            "required": ["id", "name", "email", "created_at"],
        },
        "CreateUserBody": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 5, "maxLength": 20},
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 8, "maxLength": 30},
            },
            "required": ["name", "email", "password"],
        },
        "UpdateUserPasswordBody": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "old_password": {"type": "string"},
                "new_password": {"type": "string"},
            },
            "required": ["email", "old_password", "new_password"],
        },
        "UpdateUserNameBody": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "new_name": {"type": "string", "minLength": 5, "maxLength": 20},
            },
            "required": ["email", "new_name"],
        },
        "LoginBody": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 8},
            },
            "required": ["email", "password"],
        },
        "Ingredient": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "description": {"type": "string"},
                "recipe_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
            },
        },
        "RecipePublic": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "id": {"type": "string"},
                "description": {"type": "string"},
                "instructions": {"type": "string"},
                "is_public": {"type": "boolean"},
                "ingredients": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Ingredient"},
                },
                "author_id": {"type": "string"},
                "author_name": {"type": "string"},
                "original_recipe_id": {"type": "string", "nullable": True},
                "original_author_id": {"type": "string", "nullable": True},
                "original_author_name": {"type": "string", "nullable": True},
                "created_at": {"type": "string", "format": "date-time"},
            },
        },
        "CreateIngredientBody": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "minLength": 5, "maxLength": 30},
            },
            "required": ["description"],
        },
        "CreateRecipeBody": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "maxLength": 20},
                "description": {"type": "string", "maxLength": 30},
                "instructions": {"type": "string", "maxLength": 800},
                "is_public": {"type": "boolean", "default": False},
                "ingredients": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"$ref": "#/components/schemas/CreateIngredientBody"},
                },
            },
            "required": ["title", "description", "instructions", "ingredients"],
        },
        "SaveRecipeBody": {
            "type": "object",
            "properties": {"recipe_id": {"type": "string"}},
            "required": ["recipe_id"],
        },
        "PaginationMeta": {
            "type": "object",
            "properties": {
                "page": {"type": "integer"},
                "per_page": {"type": "integer"},
                "total_items": {"type": "integer", "minimum": 0},
                "total_pages": {"type": "integer", "minimum": 0},
            },
            "required": ["page", "per_page", "total_items", "total_pages"],
        },
        "PaginatedRecipes": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/RecipePublic"},
                },
                "pagination": {"$ref": "#/components/schemas/PaginationMeta"},
            },
            "required": ["items", "pagination"],
        },
        "HttpError": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"},
                "code": {"type": "string"},
            },
        },
        "ValidationErrorBody": {
            "type": "object",
            "properties": {
                "errors": {"type": "array", "items": {"type": "object"}},
            },
        },
    }


def _paths() -> dict:
    return {
        "/": {
            "get": {
                "tags": ["Sistema"],
                "summary": "Health check",
                "responses": {"200": {"description": "API no ar", "content": {"text/plain": {"schema": {"type": "string"}}}}},
            }
        },
        "/auth/": {
            "post": {
                "tags": ["Autenticação"],
                "summary": "Login",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginBody"}}},
                },
                "responses": {
                    "200": {
                        "description": "Usuário autenticado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPublic"}}},
                    },
                    "401": {
                        "description": "Credenciais inválidas",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Payload inválido",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            }
        },
        "/users/": {
            "get": {
                "tags": ["Usuários"],
                "summary": "Listar usuários",
                "responses": {
                    "200": {
                        "description": "Lista",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/UserPublic"},
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "tags": ["Usuários"],
                "summary": "Criar usuário",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/CreateUserBody"}},
                    },
                },
                "responses": {
                    "201": {
                        "description": "Criado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPublic"}}},
                    },
                    "409": {
                        "description": "Conflito (e-mail ou nome)",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/users/{user_id}": {
            "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {
                "tags": ["Usuários"],
                "summary": "Obter usuário",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPublic"}}},
                    },
                    "404": {
                        "description": "Não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                },
            },
            "delete": {
                "tags": ["Usuários"],
                "summary": "Excluir usuário",
                "responses": {
                    "204": {"description": "Sem corpo"},
                    "404": {
                        "description": "Não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                },
            },
        },
        "/users/{user_id}/change-name": {
            "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "patch": {
                "tags": ["Usuários"],
                "summary": "Alterar nome",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/UpdateUserNameBody"}},
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPublic"}}},
                    },
                    "404": {
                        "description": "Não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "409": {
                        "description": "Conflito",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/users/{user_id}/change-password": {
            "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "patch": {
                "tags": ["Usuários"],
                "summary": "Alterar senha",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/UpdateUserPasswordBody"}},
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserPublic"}}},
                    },
                    "404": {
                        "description": "Não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "409": {
                        "description": "Senha incorreta ou regra de negócio",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/recipes/": {
            "get": {
                "tags": ["Receitas"],
                "summary": "Listar todas as receitas",
                "responses": {
                    "200": {
                        "description": "Lista",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"$ref": "#/components/schemas/RecipePublic"}},
                            }
                        },
                    },
                },
            },
            "post": {
                "tags": ["Receitas"],
                "summary": "Criar receita",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/CreateRecipeBody"}},
                    },
                },
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "responses": {
                    "201": {
                        "description": "Criada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipePublic"}}},
                    },
                    "404": {
                        "description": "Autor não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "409": {
                        "description": "Conflito de integridade",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/recipes/discover": {
            "parameters": [
                {"$ref": "#/components/parameters/UserIdHeaderOptional"},
                {"$ref": "#/components/parameters/PageQuery"},
                {"$ref": "#/components/parameters/PerPageQuery"},
            ],
            "get": {
                "tags": ["Receitas"],
                "summary": "Descobrir receitas públicas (paginado)",
                "responses": {
                    "200": {
                        "description": "Página",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedRecipes"}}},
                    },
                    "422": {
                        "description": "Query inválida",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/recipes/author/{author_id}": {
            "parameters": [
                {"name": "author_id", "in": "path", "required": True, "schema": {"type": "string"}},
                {"$ref": "#/components/parameters/PageQuery"},
                {"$ref": "#/components/parameters/PerPageQuery"},
            ],
            "get": {
                "tags": ["Receitas"],
                "summary": "Receitas do autor (paginado)",
                "responses": {
                    "200": {
                        "description": "Página",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedRecipes"}}},
                    },
                    "404": {
                        "description": "Usuário não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Query inválida",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/recipes/save": {
            "post": {
                "tags": ["Receitas"],
                "summary": "Salvar cópia de receita",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/SaveRecipeBody"}},
                    },
                },
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "responses": {
                    "201": {
                        "description": "Cópia criada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipePublic"}}},
                    },
                    "404": {
                        "description": "Receita ou usuário não encontrado",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "409": {
                        "description": "Cópia duplicada (o usuário já salvou esta receita) ou integridade",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
        },
        "/recipes/{recipe_id}": {
            "parameters": [{"name": "recipe_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {
                "tags": ["Receitas"],
                "summary": "Obter receita",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipePublic"}}},
                    },
                    "404": {
                        "description": "Não encontrada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                },
            },
            "put": {
                "tags": ["Receitas"],
                "summary": "Atualizar receita",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/CreateRecipeBody"}},
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipePublic"}}},
                    },
                    "404": {
                        "description": "Não encontrada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "409": {
                        "description": "Integridade",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "422": {
                        "description": "Validação",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
                    },
                },
            },
            "delete": {
                "tags": ["Receitas"],
                "summary": "Excluir receita",
                "responses": {
                    "204": {"description": "Sem corpo"},
                    "404": {
                        "description": "Não encontrada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                },
            },
        },
    }
