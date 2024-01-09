import unittest

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from chatbot.prompts.solar import SolarPromptTemplate


class TestSolarPromptTemplate(unittest.TestCase):
    def test_format(self):
        system_prompt = PromptTemplate(
            template="{sys}",
            input_variables=["sys"],
        )
        messages = [
            SystemMessagePromptTemplate(prompt=system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
        tmpl = SolarPromptTemplate(input_variables=["input"], messages=messages)
        history = [
            HumanMessage(content="question 1"),
            AIMessage(content="answer 1"),
        ]
        actual = tmpl.format(
            sys="system instruction", history=history, input="question 2"
        )
        expected = """<s> ### System:
system instruction</s>
<s> ### User:
question 1

### Assistant:
answer 1</s>
<s> ### User:
question 2

### Assistant:
"""
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
