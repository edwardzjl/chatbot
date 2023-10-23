import unittest

from chatbot.prompts.llama2 import prompt


class TestLLaMA2PromptTemplate(unittest.TestCase):
    def test_format(self):
        expected = """[INST] <<SYS>>
foo
<</SYS>>
bar
baz[/INST]"""
        self.assertEqual(
            prompt.format(system_message="foo", history="bar", input="baz"), expected
        )


if __name__ == "__main__":
    unittest.main()
