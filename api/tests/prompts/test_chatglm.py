import unittest

from chatbot.prompts.chatglm import prompt


class TestChatGLMPromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """foo
问: bar
答:"""
        self.assertEqual(prompt.format(history="foo", input="bar"), expected)


if __name__ == "__main__":
    unittest.main()
