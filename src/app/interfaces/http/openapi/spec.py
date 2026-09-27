"""Cookbook API — especificação OpenAPI 3.0 gerada em código (sem anotações nos blueprints)."""


def build_openapi_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Cookbook API",
            "version": "1.0.0",
            "description": (
                "Cookbook API: serviço HTTP de usuários, autenticação, receitas "
                "(públicas, privadas e descoberta) e rascunhos importados por "
                "foto via OCR.space."
            ),
        },
        "servers": [{"url": "/", "description": "Mesma origem da aplicação Flask"}],
        "tags": [
            {"name": "Sistema"},
            {"name": "Usuários"},
            {"name": "Autenticação"},
            {"name": "Receitas"},
            {"name": "Rascunhos"},
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
                "title": {"type": "string", "minLength": 1, "maxLength": 40},
                "description": {"type": "string", "minLength": 10, "maxLength": 50},
                "instructions": {"type": "string", "minLength": 10, "maxLength": 1000},
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
        "DraftIngredient": {
            "type": "object",
            "properties": {"description": {"type": "string"}},
            "required": ["description"],
        },
        "DraftPublic": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "author_id": {"type": "string"},
                "title": {"type": "string", "nullable": True},
                "description": {"type": "string", "nullable": True},
                "instructions": {"type": "string", "nullable": True},
                "ingredients": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/DraftIngredient"},
                },
                "is_draft": {"type": "boolean", "enum": [True]},
                "created_at": {"type": "string", "format": "date-time"},
            },
            "required": ["id", "author_id", "ingredients", "is_draft", "created_at"],
        },
        "CreateDraftBody": {
            "type": "object",
            "properties": {
                "source_data": {
                    "type": "string",
                    "description": (
                        "Arquivo da receita como data URI em base64. Tipos aceitos: "
                        "image/jpeg, image/png e application/pdf. Arquivo de até 1 MiB."
                    ),
                    "pattern": r"^data:(image/jpeg|image/png|application/pdf);base64,[A-Za-z0-9+/]+=*$",
                    "example": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...",
                },
            },
            "required": ["source_data"],
        },
        "UpdateDraftBody": {
            "type": "object",
            "description": (
                "Sem os limites de receita, porque o texto do OCR costuma passar "
                "deles. Os limites de receita valem ao criar a receita a partir do rascunho."
            ),
            "properties": {
                "title": {"type": "string", "nullable": True, "maxLength": 255},
                "description": {"type": "string", "nullable": True, "maxLength": 255},
                "instructions": {"type": "string", "nullable": True},
                "ingredients": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/DraftIngredient"},
                },
            },
            "required": ["ingredients"],
        },
        "PaginatedDrafts": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/DraftPublic"},
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
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
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
                    "401": {
                        "description": "O usuário não é o autor da receita",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
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
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "responses": {
                    "204": {"description": "Sem corpo"},
                    "401": {
                        "description": "O usuário não é o autor da receita",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                    "404": {
                        "description": "Não encontrada",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
                    },
                },
            },
        },
        **_draft_paths(),
    }


def _error(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HttpError"}}},
    }


def _validation_error(description: str = "Validação") -> dict:
    return {
        "description": description,
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationErrorBody"}}},
    }


def _draft_body(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DraftPublic"}}},
    }


def _draft_paths() -> dict:
    return {
        "/drafts/": {
            "get": {
                "tags": ["Rascunhos"],
                "summary": "Listar todos os rascunhos",
                "responses": {
                    "200": {
                        "description": "Lista",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"$ref": "#/components/schemas/DraftPublic"}},
                            }
                        },
                    },
                },
            },
            "post": {
                "tags": ["Rascunhos"],
                "summary": "Importar receita por foto ou PDF",
                "description": (
                    "Envia o arquivo ao OCR.space e cria um rascunho com o texto extraído. "
                    "Se o texto tiver os cabeçalhos \"Ingredientes\" e \"Modo de preparo\", "
                    "título, ingredientes e instruções são separados; caso contrário, o "
                    "texto inteiro vai para instructions."
                ),
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/CreateDraftBody"}},
                    },
                },
                "responses": {
                    "201": _draft_body("Rascunho criado"),
                    "404": _error("Usuário não encontrado"),
                    "409": _error("Conflito de integridade"),
                    "413": _error("Corpo da requisição acima do limite (MAX_CONTENT_LENGTH)"),
                    "422": {
                        "description": (
                            "Payload inválido (tipo ou formato do data URI) ou arquivo "
                            "sem texto legível (code UNREADABLE_FILE)"
                        ),
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/ValidationErrorBody"},
                                        {"$ref": "#/components/schemas/HttpError"},
                                    ]
                                }
                            }
                        },
                    },
                    "502": _error("Falha ou indisponibilidade do OCR.space"),
                },
            },
        },
        "/drafts/author/{author_id}": {
            "parameters": [
                {"name": "author_id", "in": "path", "required": True, "schema": {"type": "string"}},
                {"$ref": "#/components/parameters/PageQuery"},
                {"$ref": "#/components/parameters/PerPageQuery"},
            ],
            "get": {
                "tags": ["Rascunhos"],
                "summary": "Rascunhos do autor (paginado)",
                "responses": {
                    "200": {
                        "description": "Página",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedDrafts"}}},
                    },
                    "404": _error("Usuário não encontrado"),
                    "422": _validation_error("Query inválida"),
                },
            },
        },
        "/drafts/{draft_id}": {
            "parameters": [{"name": "draft_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {
                "tags": ["Rascunhos"],
                "summary": "Obter rascunho",
                "responses": {
                    "200": _draft_body("OK"),
                    "404": _error("Não encontrado"),
                },
            },
            "put": {
                "tags": ["Rascunhos"],
                "summary": "Atualizar rascunho",
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/UpdateDraftBody"}},
                    },
                },
                "responses": {
                    "200": _draft_body("OK"),
                    "401": _error("O usuário não é o autor do rascunho"),
                    "404": _error("Não encontrado"),
                    "409": _error("Integridade"),
                    "422": _validation_error(),
                },
            },
            "delete": {
                "tags": ["Rascunhos"],
                "summary": "Excluir rascunho",
                "description": (
                    "Também usado pelo front logo depois de POST /recipes/ quando o "
                    "rascunho vira receita."
                ),
                "parameters": [{"$ref": "#/components/parameters/UserIdHeader"}],
                "responses": {
                    "204": {"description": "Sem corpo"},
                    "401": _error("O usuário não é o autor do rascunho"),
                    "404": _error("Não encontrado"),
                    "409": _error("Integridade"),
                },
            },
        },
    }
