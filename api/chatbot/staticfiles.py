import mimetypes
import os

from fastapi import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response

from starlette.types import Scope


class CompressedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        full_path, stat_result = self.lookup_path(path)
        if stat_result is None or not os.path.isfile(full_path):
            return await super().get_response(path, scope)

        request = Request(scope)
        accept_encoding = request.headers.get("accept-encoding", "")

        encoding = None
        compressed_path = None

        if "br" in accept_encoding:
            if os.path.exists(full_path + ".br"):
                compressed_path = full_path + ".br"
                encoding = "br"
        elif "gzip" in accept_encoding:
            if os.path.exists(full_path + ".gz"):
                compressed_path = full_path + ".gz"
                encoding = "gzip"

        actual_path = compressed_path if compressed_path else full_path

        content_type, _ = mimetypes.guess_type(full_path)

        cache_control = self.get_cache_control(path)

        headers = {
            "Cache-Control": cache_control,
        }
        if encoding:
            headers["Content-Encoding"] = encoding

        return FileResponse(
            actual_path,
            headers=headers,
            media_type=content_type,
        )

    def get_cache_control(self, path: str) -> str:
        if path.endswith(".html"):
            return "no-cache"
        else:
            return "public, max-age=31536000, immutable"
