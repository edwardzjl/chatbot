from pydantic import Field

from .base import ExcludeNoneModel


class LinkResult(ExcludeNoneModel):
    title: str
    link: str


class SiteLinks(ExcludeNoneModel):
    inline: list[LinkResult] | None = None
    list_: list[LinkResult] | None = Field(alias="list", default=None)


class MustInclude(ExcludeNoneModel):
    word: str
    link: str


class OrganicResult(ExcludeNoneModel):
    """Google Light Organic Results API.

    See <https://serpapi.com/google-light-organic-results>
    """

    position: int
    """Position of the organic result on the search page"""
    title: str
    """Title of the organic result"""
    # TODO: Consider HttpUrl?
    link: str
    """Link of the organic result"""
    redirect_link: str | None = None
    """Redirect link of the organic result"""
    displayed_link: str
    """Displayed link of the organic result"""
    thumbnail: str | None = None
    """Thumbnail of the organic result"""
    date: str | None = None
    """Date of the organic result"""
    snippet: str
    """Snippet of the organic result"""
    duration: str | None = None
    """Duration of the organic result - video result"""
    sitelinks: SiteLinks | None = None
    extensions: list[str] | None = None
    rating: float | None = None
    """Item rating"""
    reviews: int | None = None
    """Number of reviews"""
    missing: list[str] | None = None
    must_include: MustInclude | None = None
