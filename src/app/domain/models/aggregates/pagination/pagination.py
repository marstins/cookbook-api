from pydantic import BaseModel


class Pagination(BaseModel):
    offset: int
    per_page: int
