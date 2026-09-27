import requests
from requests.exceptions import RequestException

from app.domain.exceptions import ExternalServiceError

_UNREADABLE = "Não foi possível extrair o texto da imagem."
_UNAVAILABLE = "O serviço de extração de texto está indisponível."


class DecodeDraftImageService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def decode_draft_image(self, source_data: str) -> str:
        if not self._api_key:
            raise ExternalServiceError(
                "O serviço de extração de texto não está configurado.",
                code="OCR_NOT_CONFIGURED",
            )

        try:
            response = requests.post(
                "https://api.ocr.space/parse/image",
                headers={"apikey": self._api_key},
                data={
                    "base64Image": source_data,
                    "language": "por",
                    "OCREngine": 3,
                    "isTable": True,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except RequestException as exc:
            raise ExternalServiceError(
                _UNAVAILABLE,
                code="OCR_UNAVAILABLE",
            ) from exc
        except ValueError as exc:
            raise ExternalServiceError(
                _UNAVAILABLE,
                code="OCR_INVALID_RESPONSE",
            ) from exc

        if payload.get("IsErroredOnProcessing"):
            raise ExternalServiceError(
                _UNREADABLE,
                code="OCR_PROCESSING_ERROR",
            )

        results = payload.get("ParsedResults") or []
        if not results:
            raise ExternalServiceError(
                _UNREADABLE,
                code="OCR_PROCESSING_ERROR",
            )

        draft_text = (results[0].get("ParsedText") or "").strip()
        if not draft_text:
            raise ExternalServiceError(
                _UNREADABLE,
                code="UNREADABLE_FILE",
            )

        return draft_text
