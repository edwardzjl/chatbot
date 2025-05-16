import unittest

from chatbot.llm_client.base import StreamThinkingProcessor


class TestStreamThinkingProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = StreamThinkingProcessor()

    def test_text_only(self):
        tokens = ["Hello", " ", "world", "!"]
        expected_chunks = [
            {"data": "Hello", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "world", "type": "text", "index": 0},
            {"data": "!", "type": "text", "index": 0},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_simple_thinking(self):
        tokens = ["<think>", "This", " ", "is", " ", "a", " ", "thought", "</think>"]
        expected_chunks = [
            {"data": "This", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "is", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "a", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "thought", "type": "thought", "index": 1},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_thinking_and_text_mixed(self):
        tokens = [
            "Before",
            " ",
            "<think>",
            "Thinking",
            " ",
            "text",
            "</think>",
            "After",
            " ",
            "thinking",
        ]
        expected_chunks = [
            {"data": "Before", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "Thinking", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "text", "type": "thought", "index": 1},
            {"data": "After", "type": "text", "index": 2},
            {"data": " ", "type": "text", "index": 2},
            {"data": "thinking", "type": "text", "index": 2},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_thinking_signature_prefix_not_tag(self):
        tokens = ["<th", "is", " ", "not", " ", "a", " ", "tag"]
        expected_chunks = [
            {
                "data": "<this",
                "type": "text",
                "index": 0,
            },  # the first two tokens will be merged
            {"data": " ", "type": "text", "index": 0},
            {"data": "not", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "a", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "tag", "type": "text", "index": 0},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_stop_thinking_signature_prefix_not_tag(self):
        tokens = ["</th", "is", " ", "also", " ", "not", " ", "a", " ", "tag"]
        expected_chunks = [
            {"data": "</th", "type": "text", "index": 0},
            {"data": "is", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "also", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "not", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "a", "type": "text", "index": 0},
            {"data": " ", "type": "text", "index": 0},
            {"data": "tag", "type": "text", "index": 0},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_consecutive_thinking_blocks(self):
        tokens = [
            "<think>",
            "First",
            " ",
            "thought",
            "</think>",
            "<think>",
            "Second",
            " ",
            "thought",
            "</think>",
        ]
        expected_chunks = [
            {"data": "First", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "thought", "type": "thought", "index": 1},
            {"data": "Second", "type": "thought", "index": 3},
            {"data": " ", "type": "thought", "index": 3},
            {"data": "thought", "type": "thought", "index": 3},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_empty_thinking_block(self):
        tokens = ["<think>", "</think>"]
        expected_chunks = []
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_thinking_tag_split_tokens(self):
        tokens = ["<th", "ink", ">", "Splitted", " ", "tag", "</", "think", ">"]
        expected_chunks = [
            {"data": "Splitted", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "tag", "type": "thought", "index": 1},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_custom_signatures(self):
        processor_custom = StreamThinkingProcessor(
            thinking_signature="[思考开始]", stop_thinking_signature="[思考结束]"
        )
        tokens = ["[思考开始]", "Custom", " ", "thinking", "[思考结束]"]
        expected_chunks = [
            {"data": "Custom", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "thinking", "type": "thought", "index": 1},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = processor_custom.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_nested_thinking_tags_not_supported(self):
        tokens = [
            "<think>",
            "Outer",
            " ",
            "<think>",
            "Inner",
            "</think>",
            " ",
            "outer",
            "</think>",
        ]
        expected_chunks = [
            {"data": "Outer", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "<think>", "type": "thought", "index": 1},
            {"data": "Inner", "type": "thought", "index": 1},
            {"data": " ", "type": "text", "index": 2},
            {"data": "outer", "type": "text", "index": 2},
            {"data": "</think>", "type": "text", "index": 2},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_thinking_tag_with_extra_content_immediately_after_start_tag(self):
        tokens = ["<think>ExtraContent", " ", "thought", "</think>"]
        expected_chunks = [
            {"data": "ExtraContent", "type": "thought", "index": 1},
            {"data": " ", "type": "thought", "index": 1},
            {"data": "thought", "type": "thought", "index": 1},
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_stop_thinking_tag_with_extra_content_immediately_after_stop_tag(self):
        tokens = [
            "<think>",
            "thought",
            "</think>ExtraContent",
        ]  # immediately after stop tag
        expected_chunks = [
            {"data": "thought", "type": "thought", "index": 1},
            {
                "data": "ExtraContent",
                "type": "text",
                "index": 2,
            },  # extra content after stop tag is still considered thought because of current logic, can adjust if needed.
        ]
        actual_chunks = []
        for token in tokens:
            chunk = self.processor.on_token(token)
            if chunk:
                actual_chunks.append(chunk)
        self.assertEqual(actual_chunks, expected_chunks)

    def test_reset_processor(self):
        tokens1 = ["<think>", "First", "</think>"]
        tokens2 = ["Text", "after", "reset"]
        processor = StreamThinkingProcessor()  # Create a new processor instance

        chunks1 = []
        for token in tokens1:
            chunk = processor.on_token(token)
            if chunk:
                chunks1.append(chunk)

        processor.reset()  # Reset the processor

        chunks2 = []
        expected_chunks2 = [
            {"data": "Text", "type": "text", "index": 0},
            {"data": "after", "type": "text", "index": 0},
            {"data": "reset", "type": "text", "index": 0},
        ]
        for token in tokens2:
            chunk = processor.on_token(token)
            if chunk:
                chunks2.append(chunk)
        self.assertEqual(
            chunks2, expected_chunks2
        )  # Assert that after reset, it processes text as text


if __name__ == "__main__":
    unittest.main()
