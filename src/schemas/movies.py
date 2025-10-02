from datetime import date
from typing import List
from pydantic import BaseModel, ConfigDict


class MovieDetailResponseSchema(BaseModel):
    id: int
    title: str
    orig_title: str
    status: str
    orig_lang: str
    budget: int
    revenue: int
    country: str
    date: date
    score: float

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: str
    next_page: str
    total_pages: int
    total_items: int

    model_config = ConfigDict(from_attributes=True)
