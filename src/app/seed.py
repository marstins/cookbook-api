"""Cookbook API: dados iniciais para a aplicação não abrir vazia."""

import click
from flask import current_app

from app.application.dto.ingredient import CreateIngredientDTO
from app.application.dto.recipe import CreateRecipeDTO
from app.application.dto.user import CreateUserDTO
from app.infrastructure.persistence.repositories import UserRepository

SEED_PASSWORD = "cookbook123"

USERS = [
    {
        "name": "Vó Maria",
        "email": "maria@cookbook.dev",
        "recipes": [
            {
                "title": "Pão de Queijo da Vó",
                "description": "Clássico mineiro de polvilho",
                "is_public": True,
                "ingredients": [
                    "500g de polvilho azedo",
                    "1 copo de água",
                    "1 copo de leite",
                    "1/2 xícara de óleo",
                    "2 ovos caipiras",
                    "100g de queijo minas ralado",
                    "Sal a gosto",
                ],
                "instructions": (
                    "Ferva a água, o leite e o óleo.\n"
                    "Escalde o polvilho e misture bem.\n"
                    "Deixe esfriar um pouco e junte os ovos e o queijo.\n"
                    "Amasse tudo com as mãos até ficar homogêneo.\n"
                    "Faça bolinhas e asse até dourar."
                ),
            },
            {
                "title": "Bolo de Fubá",
                "description": "Bolo simples para o café",
                "is_public": True,
                "ingredients": [
                    "2 xícaras de fubá",
                    "1 xícara de farinha de trigo",
                    "2 xícaras de açúcar",
                    "3 ovos",
                    "1 xícara de leite",
                    "1/2 xícara de óleo",
                    "1 colher de fermento",
                ],
                "instructions": (
                    "Bata no liquidificador os ovos, o leite, o óleo e o açúcar.\n"
                    "Misture o fubá e a farinha e depois o fermento.\n"
                    "Asse em forma untada a 180 graus por cerca de 40 minutos."
                ),
            },
        ],
    },
    {
        "name": "Chef Joao",
        "email": "joao@cookbook.dev",
        "recipes": [
            {
                "title": "Arroz de Forno",
                "description": "Aproveita as sobras do almoço",
                "is_public": True,
                "ingredients": [
                    "3 xícaras de arroz cozido",
                    "200g de presunto picado",
                    "200g de mussarela",
                    "1 caixa de creme de leite",
                    "1 lata de milho",
                ],
                "instructions": (
                    "Misture o arroz com o creme de leite, o presunto e o milho.\n"
                    "Coloque em um refratário e cubra com a mussarela.\n"
                    "Leve ao forno até o queijo derreter."
                ),
            },
            {
                "title": "Molho da Casa",
                "description": "Molho de tomate caseiro",
                "is_public": False,
                "ingredients": [
                    "6 tomates maduros",
                    "1 cebola picada",
                    "2 dentes de alho",
                    "Azeite a gosto",
                    "Manjericão fresco",
                ],
                "instructions": (
                    "Refogue a cebola e o alho no azeite.\n"
                    "Junte os tomates picados e cozinhe em fogo baixo por 30 minutos.\n"
                    "Finalize com manjericão."
                ),
            },
        ],
    },
]


@click.command("seed")
def seed_command() -> None:
    """Cria usuários e receitas de exemplo. Pode rodar mais de uma vez."""
    user_service = current_app.extensions["user_service"]
    recipe_service = current_app.extensions["recipe_service"]
    user_repository = UserRepository()

    for user_data in USERS:
        if user_repository.get_by_email(user_data["email"]):
            click.echo(f"Já existe: {user_data['email']}")
            continue

        user = user_service.create(
            CreateUserDTO(
                name=user_data["name"],
                email=user_data["email"],
                password=SEED_PASSWORD,
            )
        )
        for recipe in user_data["recipes"]:
            recipe_service.create(
                CreateRecipeDTO(
                    title=recipe["title"],
                    description=recipe["description"],
                    instructions=recipe["instructions"],
                    is_public=recipe["is_public"],
                    ingredients=[
                        CreateIngredientDTO(description=description)
                        for description in recipe["ingredients"]
                    ],
                    user_id=user.id,
                )
            )
        click.echo(f"Criado: {user_data['email']} com {len(user_data['recipes'])} receitas")

    click.echo(f"Senha dos usuários de exemplo: {SEED_PASSWORD}")
