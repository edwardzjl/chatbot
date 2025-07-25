import unittest

from chatbot.agent.token_management import (
    DEFAULT_INPUT_TOKEN_RATIO,
    DEFAULT_TOKEN_CONTEXT_LENGTH,
    MIN_POSITIVE_TOKENS,
    _calculate_max_input_tokens,
    _get_effective_token_counter,
    _get_model_max_output_tokens,
    _resolve_token_context_length,
    resolve_token_management_params,
)


class TestResolveTokenManagementParams(unittest.TestCase):
    class DummyLanguageModel:
        def get_num_tokens_from_messages(self, messages):
            return 42

        def get_context_length(self):
            return 2048

        max_tokens = 256

    def test_token_counting_full_path(self):
        model = TestResolveTokenManagementParams.DummyLanguageModel()
        result = resolve_token_management_params(model)
        counter, max_input, is_msg = result
        self.assertFalse(is_msg)
        self.assertTrue(callable(counter))
        self.assertGreater(max_input, 0)


class TestGetEffectiveTokenCounter(unittest.TestCase):
    class ChatModelWithTokenMethod:
        def get_num_tokens_from_messages(self, messages):
            return 42

    def test_explicit_token_counter(self):
        def dummy_counter(messages):
            return 999

        model = TestGetEffectiveTokenCounter.ChatModelWithTokenMethod()
        counter, is_message_counting = _get_effective_token_counter(
            model, token_counter=dummy_counter
        )

        self.assertIs(counter, dummy_counter)
        self.assertFalse(is_message_counting)

    def test_model_with_token_method(self):
        model = TestGetEffectiveTokenCounter.ChatModelWithTokenMethod()
        counter, is_message_counting = _get_effective_token_counter(model)

        self.assertTrue(callable(counter))
        self.assertEqual(counter(["msg"]), 42)
        self.assertFalse(is_message_counting)


class TestCalculateMaxInputTokens(unittest.TestCase):
    def test_valid_reservation(self):
        # 4096 - 512 = 3584
        result = _calculate_max_input_tokens(4096, 512)
        self.assertEqual(result, 3584)

    def test_reservation_exceeds_context(self):
        # 512 - 1024 = negative => fallback to ratio
        context = 512
        output = 1024
        expected = int(context * DEFAULT_INPUT_TOKEN_RATIO)
        result = _calculate_max_input_tokens(context, output)
        self.assertEqual(result, expected)

    def test_none_output_token(self):
        context = 2048
        expected = int(context * DEFAULT_INPUT_TOKEN_RATIO)
        result = _calculate_max_input_tokens(context, None)
        self.assertEqual(result, expected)

    def test_ratio_result_non_positive(self):
        # resolved_context_length so small that ratio * context < 1
        context = 1
        output = None
        result = _calculate_max_input_tokens(context, output)
        self.assertEqual(result, MIN_POSITIVE_TOKENS)


class TestResolveTokenContextLength(unittest.TestCase):
    class DummyChatModel:
        def get_context_length(self):
            return 2048

    class DummyChatModelInvalid:
        def get_context_length(self):
            return -100  # invalid

    class DummyChatModelRaises:
        def get_context_length(self):
            raise RuntimeError("mock error")

    def test_valid_user_context_length(self):
        model = TestResolveTokenContextLength.DummyChatModel()
        result = _resolve_token_context_length(model, 1024)
        self.assertEqual(result, 1024)

    def test_invalid_user_context_length_model_valid(self):
        model = TestResolveTokenContextLength.DummyChatModel()
        result = _resolve_token_context_length(model, -1)
        self.assertEqual(result, 2048)

    def test_invalid_user_context_length_model_invalid(self):
        model = TestResolveTokenContextLength.DummyChatModelInvalid()
        result = _resolve_token_context_length(model, -1)
        self.assertEqual(result, DEFAULT_TOKEN_CONTEXT_LENGTH)

    def test_user_context_none_model_valid(self):
        model = TestResolveTokenContextLength.DummyChatModel()
        result = _resolve_token_context_length(model, None)
        self.assertEqual(result, 2048)

    def test_user_context_none_model_invalid(self):
        model = TestResolveTokenContextLength.DummyChatModelInvalid()
        result = _resolve_token_context_length(model, None)
        self.assertEqual(result, DEFAULT_TOKEN_CONTEXT_LENGTH)

    def test_user_context_none_model_raises(self):
        model = TestResolveTokenContextLength.DummyChatModelRaises()
        result = _resolve_token_context_length(model, None)
        self.assertEqual(result, DEFAULT_TOKEN_CONTEXT_LENGTH)

    def test_user_context_none_model_lacks_method(self):
        model = object()  # no get_context_length
        result = _resolve_token_context_length(model, None)
        self.assertEqual(result, DEFAULT_TOKEN_CONTEXT_LENGTH)


class TestGetModelMaxOutputTokens(unittest.TestCase):
    class ChatModelWithValidMaxTokens:
        max_tokens = 128

    class ChatModelWithInvalidMaxTokens:
        max_tokens = -1

    class ChatModelWithNoneMaxTokens:
        max_tokens = None

    class ChatModelRaises:
        @property
        def max_tokens(self):
            raise RuntimeError("mock error")

    def test_valid_max_tokens(self):
        model = TestGetModelMaxOutputTokens.ChatModelWithValidMaxTokens()
        result = _get_model_max_output_tokens(model)
        self.assertEqual(result, 128)

    def test_invalid_max_tokens(self):
        model = TestGetModelMaxOutputTokens.ChatModelWithInvalidMaxTokens()
        result = _get_model_max_output_tokens(model)
        self.assertIsNone(result)

    def test_none_max_tokens(self):
        model = TestGetModelMaxOutputTokens.ChatModelWithNoneMaxTokens()
        result = _get_model_max_output_tokens(model)
        self.assertIsNone(result)

    def test_raises_exception(self):
        model = TestGetModelMaxOutputTokens.ChatModelRaises()
        result = _get_model_max_output_tokens(model)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
