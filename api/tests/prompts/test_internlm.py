import unittest

from chatbot.prompts.internlm import prompt


class TestInternLMPromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """A chat between a curious <|User|> and an <|Bot|>. The <|Bot|> gives helpful, detailed, and polite answers to the <|User|>'s questions.


foo
<s><|User|>:bar<eoh>
<|Bot|>:"""
        self.assertEqual(prompt.format(history="foo", input="bar"), expected)


if __name__ == "__main__":
    unittest.main()
