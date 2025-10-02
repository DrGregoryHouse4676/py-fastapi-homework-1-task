from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db, MovieModel
from src.schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter(prefix="/movies")


@router.get("/", response_model=MovieListResponseSchema, name="get_movies")
async def get_movies(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> MovieListResponseSchema:
    total_items: int = await db.scalar(select(func.count(MovieModel.id))) or 0

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    offset = (page - 1) * per_page
    if offset >= total_items:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = ceil(total_items / per_page)

    movies_result = await db.execute(
        select(MovieModel)
        .order_by(MovieModel.id)
        .offset(offset)
        .limit(per_page)
    )
    movies = movies_result.scalars().all()

    base_path = request.url_for("get_movies").path

    prev_page = f"{base_path}?page={max(1, page - 1)}&per_page={per_page}"
    next_page = f"{base_path}?page={min(total_pages, page + 1)}&per_page={per_page}"

    return MovieListResponseSchema(
        movies=[MovieDetailResponseSchema.model_validate(m) for m in movies],
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovieDetailResponseSchema:
    movie = await db.get(MovieModel, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)
