import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from aiohttp import ClientResponseError
from requests import RequestException

from chatbot.llm.providers import (
    get_model_info,
    get_num_tokens_vllm,
    get_num_tokens_tgi,
)


class TestGetModelInfo(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.base_url = "http://fake-server"
        self.model_name = "test-model"

    async def _mock_session_context(
        self,
        url_map: dict[
            tuple[str, str], dict[str, Any]
        ],  # (method, url) -> {json?, text?, status?, headers?, etc}
    ) -> AsyncMock:
        async def mock_request(method: str, url: str, *args, **kwargs):
            response_data = url_map.get((method.upper(), url), {})

            response = AsyncMock()
            if "json" in response_data:
                response.json.return_value = response_data["json"]
            if "text" in response_data:
                response.text.return_value = response_data["text"]
            if "status" in response_data:
                response.status = response_data["status"]
            if "headers" in response_data:
                response.headers = response_data["headers"]

            context = AsyncMock()
            context.__aenter__.return_value = response
            return context

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value.request.side_effect = mock_request

        for method in ["get", "post", "put", "delete"]:
            setattr(
                mock_session.__aenter__.return_value,
                method,
                lambda url, *args, method=method, **kwargs: mock_request(
                    method, url, *args, **kwargs
                ),
            )

        return mock_session

    @patch("chatbot.llm.providers.AsyncCachedSession")
    async def test_owned_by(self, mock_session_ctx: MagicMock) -> None:
        mock_session_ctx.return_value = await self._mock_session_context(
            {
                ("GET", "/v1/models"): {
                    "json": {"data": [{"id": self.model_name, "owned_by": "vllm"}]},
                    "status": 200,
                }
            }
        )
        result = await get_model_info(self.base_url, self.model_name)
        self.assertEqual(result["owned_by"], "vllm")

    @patch("chatbot.llm.providers.AsyncCachedSession")
    async def test_owned_by_sglang_with_server_info(
        self, mock_session_ctx: MagicMock
    ) -> None:
        mock_session_ctx.return_value = await self._mock_session_context(
            {
                ("GET", "/v1/models"): {
                    "json": {"data": [{"id": self.model_name, "owned_by": "sglang"}]},
                    "status": 200,
                },
                ("GET", "/get_server_info"): {
                    "json": {"version": "1.2.3"},
                    "status": 200,
                },
            }
        )
        result = await get_model_info(self.base_url, self.model_name)
        self.assertIn("server_info", result)
        self.assertEqual(result["server_info"]["version"], "1.2.3")

    @patch("chatbot.llm.providers.AsyncCachedSession")
    async def test_unknown_owned_by_assume_tgi(
        self, mock_session_ctx: MagicMock
    ) -> None:
        mock_session_ctx.return_value = await self._mock_session_context(
            {
                ("GET", "/v1/models"): {
                    "json": {
                        "data": [{"id": self.model_name, "owned_by": self.model_name}]
                    },
                    "status": 200,
                },
                ("GET", "/info"): {
                    "json": {"model_id": self.model_name},
                    "status": 200,
                },
            }
        )
        result = await get_model_info(self.base_url, self.model_name)
        self.assertIn("info", result)
        self.assertEqual(result["info"]["model_id"], self.model_name)

    @patch("chatbot.llm.providers.AsyncCachedSession")
    async def test_model_not_found(self, mock_session_ctx: MagicMock) -> None:
        mock_session_ctx.return_value = await self._mock_session_context(
            {
                ("GET", "/v1/models"): {
                    "json": {"data": []},
                    "status": 200,
                }
            }
        )

        result = await get_model_info(self.base_url, self.model_name)
        self.assertEqual(result, {})

    @patch("chatbot.llm.providers.AsyncCachedSession")
    async def test_http_error(self, mock_session_ctx: MagicMock) -> None:
        session = MagicMock()
        session.get.side_effect = ClientResponseError(request_info=None, history=None)

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = session
        mock_session_ctx.return_value = mock_session

        with self.assertRaises(ClientResponseError):
            await get_model_info(self.base_url, self.model_name)


class TestGetTokens(unittest.TestCase):
    @patch("requests.post")
    def test_get_num_tokens_vllm(self, mock_post: MagicMock) -> None:
        # Mock a successful post response for vllm
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 150}
        mock_post.return_value = mock_response

        result = get_num_tokens_vllm(
            "http://vllm.provider", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 150)

    @patch("requests.post")
    def test_get_num_tokens_tgi(self, mock_post: MagicMock) -> None:
        # Mock a successful post response for TGI
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tokenize_response": [1, 2, 3]}
        mock_post.return_value = mock_response

        result = get_num_tokens_tgi(
            "http://tgi.provider", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 3)

    @patch("requests.post")
    def test_get_num_tokens_error(self, mock_post: MagicMock) -> None:
        # Simulate a RequestException in tokenization functions
        mock_post.side_effect = RequestException("Error in tokenization")

        result = get_num_tokens_vllm(
            "http://fakeurl.com", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 2)  # Falls back to message count (len)

        result = get_num_tokens_tgi(
            "http://fakeurl.com", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 2)  # Falls back to message count (len)


if __name__ == "__main__":
    unittest.main()
