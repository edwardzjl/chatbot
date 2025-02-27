import unittest

from chatbot.utils import StreamThinkingProcessor


class TestStreamThinkingProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = StreamThinkingProcessor()

    def test_text_only(self):
        tokens = ["Hello", " ", "world", "!"]
        expected_chunks = [
            {"data": "Hello", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "world", "type": "text"},
            {"data": "!", "type": "text"},
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
            {"data": "This", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "is", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "a", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "thought", "type": "thought"},
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
            {"data": "Before", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "Thinking", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "text", "type": "thought"},
            {"data": "After", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "thinking", "type": "text"},
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
            {"data": "<this", "type": "text"},  # the first two tokens will be merged
            {"data": " ", "type": "text"},
            {"data": "not", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "a", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "tag", "type": "text"},
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
            {"data": "</th", "type": "text"},
            {"data": "is", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "also", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "not", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "a", "type": "text"},
            {"data": " ", "type": "text"},
            {"data": "tag", "type": "text"},
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
            {"data": "First", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "thought", "type": "thought"},
            {"data": "Second", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "thought", "type": "thought"},
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
            {"data": "Splitted", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "tag", "type": "thought"},
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
            {"data": "Custom", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "thinking", "type": "thought"},
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
            {"data": "Outer", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "<think>", "type": "thought"},
            {"data": "Inner", "type": "thought"},
            {"data": " ", "type": "text"},
            {"data": "outer", "type": "text"},
            {"data": "</think>", "type": "text"},
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
            {"data": "ExtraContent", "type": "thought"},
            {"data": " ", "type": "thought"},
            {"data": "thought", "type": "thought"},
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
            {"data": "thought", "type": "thought"},
            {
                "data": "ExtraContent",
                "type": "text",
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
            {"data": "Text", "type": "text"},
            {"data": "after", "type": "text"},
            {"data": "reset", "type": "text"},
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
