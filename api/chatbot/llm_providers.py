from __future__ import annotations

from functools import partial, lru_cache
from typing import Any, Callable
from urllib.parse import urljoin

import requests
from langchain_core.messages.utils import convert_to_openai_messages
from loguru import logger


# TODO: we can support async here, but I'm not explicitly depending on `aiohttp` yet.
@lru_cache
def get_model_info(base_url: str, model_name: str) -> dict[str, Any]:
    """Fetches information about a model from the model provider.

    Different model provider may have different schemas. Instead of maintaining a common schema,
    each provider's response is returned as-is within a dictionary.

    Args:
        base_url (str): The base URL of the model server.
        model_name (str): The name or ID of the model whose information is to be fetched.

    Returns:
        dict[str, Any]: A dictionary containing the model information. The structure of the dictionary depends on the provider's response.

    Raises:
        requests.RequestException: If any error occurs while making the HTTP request to fetch model information.

    Notes:
        - The function currently handles model servers owned by `vllm`, `llamacpp`, `sglang` and `TGI`, with specific handling for each.
        - For the `TGI` server type, the function checks for the existence of the `/info` endpoint, as there is no definitive way to identify a `TGI` server beforehand.
        - The function is designed to be extendable for more model providers in the future.
    """
    try:
        # Get general model info
        resp = requests.get(urljoin(base_url, "/v1/models"))
        resp.raise_for_status()
        models = resp.json().get("data", [])
        model_info = next((item for item in models if item["id"] == model_name), {})
        # Handle specific providers
        match model_info.get("owned_by"):
            case "vllm" | "llamacpp":
                return model_info
            case "sglang":
                # <https://sgl-project.github.io/backend/native_api.html#Get-Server-Info>
                resp = requests.get(urljoin(base_url, "/get_server_info"))
                resp.raise_for_status()
                server_info = resp.json()
                model_info["server_info"] = server_info
                return model_info
            case _:
                # TODO: Check more servers.
                # NOTE: TGI(3.0.1) also falls into this category, as the 'owned_by' of TGI services to be model id and is not customizable.
                # <https://huggingface.github.io/text-generation-inference/#/Text%20Generation%20Inference/get_model_info>
                resp = requests.get(urljoin(base_url, "/info"))
                resp.raise_for_status()
                info = resp.json()
                model_info["info"] = info
                return model_info
    except requests.RequestException:
        logger.warning("Error fetching model info for {} from {}", model_name, base_url)
        raise


@lru_cache
def get_truncation_config(
    base_url: str, model_name: str
) -> tuple[int, Callable[[list], int]]:
    """Fetches the truncation configuration for a given model.

    This function attempts to retrieve the maximum token count (`max_tokens`) and a function to
    count tokens (`token_counter`) for a given model. If any of these cannot be retrieved, the
    function falls back to truncating messages based on the message count (`len`). Note that the
    fallback may lead to context overflow.

    Args:
        base_url (str): The base URL of the model server.
        model_name (str): The name or ID of the model for which truncation config is to be fetched.

    Returns:
        tuple[int, Callable[[list], int]]: A tuple where the first element is the maximum token count
        for the model, and the second element is a function that takes a list of messages and returns the
        number of tokens in those messages. Defaults to `(20, len)` in case of errors or missing data.
    """
    try:
        max_tokens = get_max_tokens(base_url, model_name)
        if max_tokens is None:
            logger.warning(
                "Could not get max tokens from provider, will truncate messages by message count. This may lead to context overflow."
            )
            return 20, len
        token_counter = get_num_tokens_func(base_url, model_name)
        if token_counter is None:
            logger.warning(
                "Could not get token counter function from provider, will truncate messages by message count. This may lead to context overflow."
            )
            return 20, len
        return max_tokens, token_counter
    except Exception:
        logger.exception(
            "Error while fetching truncation config for model '{}' from provider '{}'. Falling back to message count truncation.",
            model_name,
            base_url,
        )
        return 20, len


@lru_cache
def get_max_tokens(base_url: str, model_name: str) -> int | None:
    """Fetches the maximum token length for a given model.

    If the information cannot be retrieved or the model provider is unknown, the function
    returns `None` to indicate that the maximum token length is unavailable.

    Args:
        base_url (str): The base URL of the model server.
        model_name (str): The name or ID of the model whose max token length is to be fetched.

    Returns:
        int | None: The maximum number of tokens that the model can handle, or `None` if unavailable.

    Raises:
        KeyError

    Notes:
        - Supports model providers: `vllm`, `llamacpp`, `sglang`, and TGI (for which additional details may need to be added).
        - Returns `None` if max token length is not found or if an error occurs during fetching model info.
    """
    try:
        # NOTE: as `get_model_info` returns a dict, I cannot make it a 'dependency' with `lru_cache`.
        model_info = get_model_info(base_url, model_name)
    except requests.RequestException:
        logger.warning("Error loading model info, using `None` as max tokens")
        return None

    # Extract the max token length based on the model provider
    match model_info.get("owned_by"):
        case "vllm":
            return model_info.get("max_model_len")
        case "llamacpp":
            return model_info.get("meta", {}).get("n_ctx_train")
        case "sglang":
            return model_info.get("server_info", {}).get("max_total_num_tokens")
        case _:
            # TODO: Check more servers.
            # NOTE: TGI(3.0.1) also falls into this category, as the 'owned_by' of TGI services to be model id and is not customizable.
            return model_info.get("info", {}).get("max_total_tokens")


@lru_cache
def get_num_tokens_func(base_url: str, model_name: str) -> Callable[[list], int] | None:
    """Returns a function to calculate the number of tokens for a given model.

    This function checks the model provider (e.g., vllm, llamacpp, sglang) and returns the appropriate
    function for token counting.

    Args:
        base_url (str): The base URL of the model server.
        model_name (str): The name or ID of the model whose token count function is to be fetched.

    Returns:
        Callable[[list], int] | None: A callable function that takes a list of messages and returns the
        number of tokens, or `None` if no function is available for the provider.

    Raises:
        requests.RequestException: If there is an error in retrieving model info.
    """
    model_info = get_model_info(base_url, model_name)

    match model_info.get("owned_by"):
        case "vllm":
            return partial(get_num_tokens_vllm, base_url, model_name)
        case "llamacpp":
            # llama.cpp (b4367) only supports tokenize text, not chat messages.
            logger.warning(
                "Tokenization not supported for {} (llamacpp provider).", model_name
            )
            return None
        case "sglang":
            # SGLang (0.4.0) does not have a dedicated endpoint for tokenization.
            logger.warning(
                "Tokenization not supported for {} (sglang provider).", model_name
            )
            return None
        case _:
            # TODO: Check more servers.
            # NOTE: TGI(3.0.1) falls into this category, as the 'owned_by' of TGI services to be model id and is not customizable.
            logger.warning(
                "Tokenization function fallback for {} (unknown provider).", model_name
            )
            return partial(get_num_tokens_tgi, base_url, model_name)


# NOTE: langchain's `get_num_tokens_from_messages` does not support async


def get_num_tokens_vllm(base_url: str, model_name: str, messages: list) -> int:
    """Get the number of tokens for a list of messages using vllm provider.

    Args:
        base_url (str): The base URL of the vllm server.
        model_name (str): The name or ID of the vllm model.
        messages (list): A list of messages to tokenize.

    Returns:
        int: The number of tokens in the provided messages.
    """
    url = urljoin(base_url, "/tokenize")
    # use 'prompt' param instead of 'messages' to get the number of tokens in the prompt
    try:
        resp = requests.post(
            url,
            json={
                "model": model_name,
                "messages": convert_to_openai_messages(messages),
            },
        )
        resp.raise_for_status()
        return resp.json()["count"]
    except requests.RequestException:
        logger.error(
            "Error tokenizing messages for {} at {}, fallback to message count.",
            model_name,
            base_url,
        )
        # Default to the length of messages if there is an error
        return len(messages)


def get_num_tokens_tgi(base_url: str, model_name: str, messages: list) -> int:
    """Get the number of tokens for a list of messages using TGI provider.

    Args:
        base_url (str): The base URL of the TGI server.
        model_name (str): The name or ID of the TGI model.
        messages (list): A list of messages to tokenize.

    Returns:
        int: The number of tokens in the provided messages.
    """
    url = urljoin(base_url, "/chat_tokenize")
    try:
        resp = requests.post(
            url,
            json={
                "model": model_name,
                "messages": convert_to_openai_messages(messages),
            },
        )
        resp.raise_for_status()
        return len(resp.json()["tokenize_response"])
    except requests.RequestException:
        logger.error(
            "Error tokenizing messages for {} at {}, fallback to message count.",
            model_name,
            base_url,
        )
        # Default to the length of messages if there is an error
        return len(messages)
