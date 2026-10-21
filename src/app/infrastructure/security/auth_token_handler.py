import time
from typing import Any

from auth0.authentication.exceptions import TokenValidationError
from auth0.authentication.token_verifier import AsymmetricSignatureVerifier, TokenVerifier

from app.domain.exceptions import UnauthorizedError


class AuthTokenHandler:
    def __init__(self, domain: str, audience: str, client_id: str) -> None:
        signature_verifier = AsymmetricSignatureVerifier(
            f"https://{domain}/.well-known/jwks.json",
            cache_ttl=60 * 60 * 24
        )
        self._issuer = f"https://{domain}/"
        self._audience = audience
        self._signature_verifier = signature_verifier
        self._id_token_verifier = TokenVerifier(
            signature_verifier,
            issuer=self._issuer,
            audience=client_id,
        )

    def decode(self, token: str) -> dict[str, Any]:
        try:
            payload = self._signature_verifier.verify_signature(token)
            self._verify_access_token(payload)
            return payload
        except TokenValidationError as exc:
            raise self._unauthorized_from_validation_error(exc) from exc

    def decode_id_token(self, token: str) -> dict[str, Any]:
        try:
            return self._id_token_verifier.verify(token)
        except TokenValidationError as exc:
            raise self._unauthorized_from_validation_error(exc) from exc

    def _verify_access_token(self, payload: dict[str, Any]) -> None:
        if "iss" not in payload or not isinstance(payload["iss"], str):
            raise TokenValidationError("Issuer (iss) claim must be a string present in the token")
        if payload["iss"] != self._issuer:
            raise TokenValidationError(
                f'Issuer (iss) claim mismatch; expected "{self._issuer}", found "{payload["iss"]}"'
            )

        if "sub" not in payload or not isinstance(payload["sub"], str):
            raise TokenValidationError("Subject (sub) claim must be a string present in the token")

        aud = payload.get("aud")
        if not isinstance(aud, (str, list)):
            raise TokenValidationError("Audience (aud) claim must be a string or array of strings")
        if isinstance(aud, list):
            if self._audience not in aud:
                raise TokenValidationError("Audience (aud) claim mismatch")
        elif aud != self._audience:
            raise TokenValidationError("Audience (aud) claim mismatch")

        if "exp" not in payload or not isinstance(payload["exp"], int):
            raise TokenValidationError("Expiration Time (exp) claim must be a number present in the token")
        if time.time() > payload["exp"]:
            raise TokenValidationError("Expiration Time (exp) claim error")

    @staticmethod
    def _unauthorized_from_validation_error(exc: TokenValidationError) -> UnauthorizedError:
        if "Expiration Time" in str(exc):
            return UnauthorizedError("Token expirado.", code="TOKEN_EXPIRED")
        return UnauthorizedError("Token inválido.", code="INVALID_TOKEN")
