import jwt

from typing import Any

from auth0.authentication import Database, GetToken
from auth0.authentication.exceptions import Auth0Error
from auth0.management import ManagementClient
from auth0.management.core.api_error import ApiError

from app.domain.exceptions import ConflictError, ExternalServiceError, UnauthorizedError


class Auth0Client:
    def __init__(self, domain: str, client_id: str, client_secret: str, db_name: str) -> None:
        self._domain = domain
        self._db_name = db_name
        self._token_client = GetToken(domain, client_id, client_secret)
        self._database_client = Database(domain, client_id, client_secret)
        self._management_client = ManagementClient(domain=domain, client_id=client_id, client_secret=client_secret)
        self._token_scope = "openid email profile offline_access"
        self._token_audience = "https://cookbook-api"


    def signup(self, email: str, password: str) -> dict[str, Any]:
        try:
            return self._database_client.signup(email, password, self._db_name)
        except Auth0Error as exc:
            if exc.error_code in {"user_exists", "username_exists"} or (
                exc.error_code == "invalid_signup" and "already exists" in exc.message.lower()
            ):
                raise ConflictError(
                    "E-mail ou nome de usuário já cadastrado.",
                    code="USER_ALREADY_EXISTS",
                ) from exc
            if exc.error_code in {
                "invalid_password",
                "password_strength_error",
                "password_dictionary_error",
                "password_no_user_info_error",
            }:
                raise ConflictError(
                    "A senha não atende aos requisitos.",
                    code="INVALID_PASSWORD",
                ) from exc
            raise ExternalServiceError(
                "Não foi possível criar a conta.",
                code="AUTH0_SIGNUP_FAILED",
            ) from exc


    def login(self, email: str, password: str) -> dict[str, Any]:
        try:
            tokens = self._token_client.login(
                username=email,
                password=password,
                realm=self._db_name,
                audience=self._token_audience,
                scope=self._token_scope,
            )
        except Auth0Error as exc:
            if exc.error_code == "invalid_grant":
                raise UnauthorizedError(
                    "Credenciais inválidas",
                    code="INVALID_CREDENTIALS",
                ) from exc
            raise ExternalServiceError(
                "Erro ao realizar login.",
                code="AUTH0_UNAVAILABLE",
            ) from exc

        return tokens


    def change_password(self, auth_id: str, email: str, old_password: str, new_password: str) -> dict[str, Any]:
        try:
            self._token_client.login(username=email, password=old_password, realm=self._db_name)
        except Auth0Error as exc:
            if exc.error_code == "invalid_grant":
                raise UnauthorizedError(
                    "Credenciais inválidas",
                    code="INVALID_CREDENTIALS",
                ) from exc
            raise ExternalServiceError(
                "Não foi possível validar a senha atual.",
                code="AUTH0_UNAVAILABLE",
            ) from exc

        try:
            self._management_client.users.update(auth_id, password=new_password)
        except ApiError as exc:
            raise ExternalServiceError(
                "Não foi possível atualizar a senha.",
                code="AUTH0_PASSWORD_UPDATE_FAILED",
            ) from exc

        try:
            updated_tokens = self._token_client.login(
                email,
                new_password,
                realm=self._db_name,
                audience="https://cookbook-api",
                scope=self._token_scope
            )
        except Auth0Error as exc:
            raise ExternalServiceError(
                "Erro autenticando usuário com nova senha.",
                code="AUTH0_TOKEN_ISSUE_FAILED",
            ) from exc

        return updated_tokens


    def refresh_token(self, token: str) -> dict[str, Any]:
        try:
            return self._token_client.refresh_token(token, self._token_scope)
        except Auth0Error as exc:
            if exc.error_code == "invalid_grant":
                raise UnauthorizedError(
                    "Sessão expirada.",
                    code="TOKEN_EXPIRED",
                ) from exc
            raise ExternalServiceError(
                "Não foi possível renovar a sessão.",
                code="AUTH0_UNAVAILABLE",
            ) from exc


    def get_users_by_email(self, email: str) -> list[dict[str, Any]]:
        return self._management_client.users.list_users_by_email(
            include_fields=True,
            email=email,
        )

