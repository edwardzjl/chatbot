import unittest

from chatbot.prompts.vicuna import prompt


class TestVicunaPromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.

foo
USER: bar
ASSISTANT:"""
        self.assertEqual(prompt.format(history="foo", input="bar"), expected)


if __name__ == "__main__":
    unittest.main()
