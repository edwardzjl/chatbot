import unittest

from chatbot.prompts.baichuan import prompt


class TestBaichuanPromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """foo
 <reserved_102> : bar
 <reserved_103> :"""
        self.assertEqual(prompt.format(history="foo", input="bar"), expected)


if __name__ == "__main__":
    unittest.main()
