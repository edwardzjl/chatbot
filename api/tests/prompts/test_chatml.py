import unittest

from chatbot.prompts.chatml import prompt


class TestChatMLPromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """<|im_start|>system
foo<|im_end|>

bar
<|im_start|>user
baz<|im_end|>
<|im_start|>assistant
"""
        self.assertEqual(
            prompt.format(system_message="foo", history="bar", input="baz"), expected
        )


if __name__ == "__main__":
    unittest.main()
