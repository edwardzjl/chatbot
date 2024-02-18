from langchain.chains import LLMChain
from langchain_core.prompts import (
    BasePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from chatbot.prompts.chatml import ChatMLPromptTemplate

instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively.
Knowledge cutoff: 2023-10-01
Current date: {date}
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""
messages = [
    SystemMessagePromptTemplate.from_template(instruction),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
]
tmpl = ChatMLPromptTemplate(input_variables=["date", "input"], messages=messages)


class ConversationChain(LLMChain):
    """Conversation chain that disables persists messages to memory.
    I handle the memory saving myself."""

    prompt: BasePromptTemplate = tmpl

    def prep_outputs(
        self,
        inputs: dict[str, str],
        outputs: dict[str, str],
        return_only_outputs: bool = False,
    ) -> dict[str, str]:
        """Override this method to disable saving context to memory."""
        self._validate_outputs(outputs)
        if return_only_outputs:
            return outputs
        else:
            return {**inputs, **outputs}
