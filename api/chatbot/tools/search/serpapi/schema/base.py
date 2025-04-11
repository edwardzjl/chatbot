from typing import Any

from pydantic import BaseModel


class ExcludeNoneModel(BaseModel):
    """Base model to exclude None values when dumping."""

    def model_dump(self, *, exclude_none: bool = True, **kwargs) -> dict[str, Any]:
        return super().model_dump(exclude_none=exclude_none, **kwargs)

    def model_dump_json(self, *, exclude_none: bool = True, **kwargs) -> str:
        return super().model_dump_json(exclude_none=exclude_none, **kwargs)
