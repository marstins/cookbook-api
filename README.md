# Cookbook API

API HTTP para cadastro de usuários, autenticação e receitas da aplicação Cookbook.

## Executar

Na raiz do repositório (`cookbook-api`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Subir o Flask (sempre na raiz do repositório, com o `PYTHONPATH` apontando para `src`):

```bash
export PYTHONPATH=src
flask --app app.app run --debug
```

Ou em uma linha:

```bash
PYTHONPATH=src flask --app app.app run --debug
```

Documentação interativa (Swagger UI): **http://127.0.0.1:5000/docs** — o JSON OpenAPI está em **/openapi.json**.

No Windows, ao ativar a venv use `.venv\Scripts\activate` em vez de `source .venv/bin/activate`.
