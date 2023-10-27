import unittest

from chatbot.prompts.llama2 import prompt


class TestLLaMA2PromptTemplate(unittest.TestCase):
    def test_format_first_round(self):
        # TODO: there will be a whitespace before the first user message that I cannot elegantly remove now.
        expected = """<s>[INST] <<SYS>>
foo
<</SYS>>

 bar [/INST]"""
        self.assertEqual(
            prompt.format(system_message="foo", history="", input="bar"), expected
        )

    def test_format_second_round(self):
        expected = """<s>[INST] <<SYS>>
foo
<</SYS>>

bar [/INST] foobar </s><s>[INST] baz [/INST]"""
        self.assertEqual(
            prompt.format(
                system_message="foo",
                history="bar [/INST] foobar </s><s>[INST]",
                input="baz",
            ),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
