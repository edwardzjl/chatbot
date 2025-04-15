import unittest
from unittest.mock import patch, Mock

import requests

from chatbot.llm.providers import (
    get_model_info,
    get_num_tokens_vllm,
    get_num_tokens_tgi,
)


class TestGetModelInfo(unittest.TestCase):
    @patch("requests.get")
    def test_get_model_info_vllm(self, mock_get):
        # Mock the response for a successful model info fetch
        mock_response = Mock(requests.models.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": "test_model", "owned_by": "vllm", "max_model_len": 4096}]
        }
        mock_get.return_value = mock_response

        result = get_model_info("http://vllm.provider", "test_model")
        self.assertEqual(result.get("owned_by"), "vllm")
        self.assertEqual(result.get("max_model_len"), 4096)

    @patch("requests.get")
    def test_get_model_info_sglang(self, mock_get):
        # Mock response for SGLang provider
        mock_response = Mock(requests.models.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": "test_model", "owned_by": "sglang"}]
        }
        mock_get.return_value = mock_response

        # Simulating a second request for "/get_server_info"
        mock_server_info_response = Mock(requests.models.Response)
        mock_server_info_response.status_code = 200
        mock_server_info_response.json.return_value = {"max_total_num_tokens": 2048}
        with patch(
            "requests.get", side_effect=[mock_response, mock_server_info_response]
        ):
            result = get_model_info("http://sglang.provider", "test_model")
            self.assertEqual(result.get("owned_by"), "sglang")
            self.assertEqual(
                result.get("server_info", {}).get("max_total_num_tokens"), 2048
            )

    @patch("requests.get")
    def test_get_model_info_error(self, mock_get):
        # Simulate a request exception
        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(requests.RequestException):
            get_model_info("http://fakeurl.com", "test_model")


class TestGetTokens(unittest.TestCase):
    @patch("requests.post")
    def test_get_num_tokens_vllm(self, mock_post):
        # Mock a successful post response for vllm
        mock_response = Mock(requests.models.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 150}
        mock_post.return_value = mock_response

        result = get_num_tokens_vllm(
            "http://vllm.provider", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 150)

    @patch("requests.post")
    def test_get_num_tokens_tgi(self, mock_post):
        # Mock a successful post response for TGI
        mock_response = Mock(requests.models.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"tokenize_response": [1, 2, 3]}
        mock_post.return_value = mock_response

        result = get_num_tokens_tgi(
            "http://tgi.provider", "test_model", ["message1", "message2"]
        )
        self.assertEqual(result, 3)

    @patch("requests.post")
    def test_get_num_tokens_error(self, mock_post):
        # Simulate a RequestException in tokenization functions
        mock_post.side_effect = requests.RequestException("Error in tokenization")

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
