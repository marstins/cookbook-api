import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DEFAULT_SQLITE = (_REPO_ROOT / "instance" / "app.sqlite").resolve()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"sqlite:///{_DEFAULT_SQLITE.as_posix()}"
    )
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGINATION_DEFAULT_PER_PAGE = int(
        os.environ.get("PAGINATION_DEFAULT_PER_PAGE", "10")
    )
    PAGINATION_MAX_PER_PAGE = int(
        os.environ.get("PAGINATION_MAX_PER_PAGE", "100")
    )
    # Teto do arquivo cru (OCR.space free: 1 MiB). O corpo HTTP é data URI
    # em JSON; base64 infla ~33%, mais o envelope {"source_data":"..."}.
    MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(1 * 1024 * 1024)))
    MAX_CONTENT_LENGTH = int(MAX_UPLOAD_BYTES * 4 / 3) + 1024
