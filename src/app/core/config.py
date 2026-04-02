import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DEFAULT_SQLITE = (_REPO_ROOT / "instance" / "app.sqlite").resolve()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"sqlite:///{_DEFAULT_SQLITE.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGINATION_DEFAULT_PER_PAGE = int(
        os.environ.get("PAGINATION_DEFAULT_PER_PAGE", "10")
    )
    PAGINATION_MAX_PER_PAGE = int(
        os.environ.get("PAGINATION_MAX_PER_PAGE", "100")
    )
