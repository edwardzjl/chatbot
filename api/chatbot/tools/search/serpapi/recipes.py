from pydantic import HttpUrl

from .schema.base import ExcludeNoneModel


# TODO: WIP
class RecipesResult(ExcludeNoneModel):
    """SerperApi recipes result schema.

    See <https://serpapi.com/recipes-results>
    """

    title: str
    link: HttpUrl
    source: str
    rating: float
    total_time: str
    ingredients: list[str] | None = None
