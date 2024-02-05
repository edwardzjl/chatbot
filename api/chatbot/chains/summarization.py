from langchain.chains import LLMChain
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from langchain_core.prompts import (
    BasePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from chatbot.prompts.chatml import ChatMLPromptTemplate

system_prompt = """You are Rei, the ideal assistant dedicated to assisting users effectively.
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""
messages = [
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="history"),
    SystemMessagePromptTemplate.from_template(
        "Now Provide a short title of the conversation in less than 10 words."
    ),
]
tmpl = ChatMLPromptTemplate(input_variables=[], messages=messages)


class SummarizationChain(LLMChain):

    prompt: BasePromptTemplate = tmpl
    output_key: str = "summary"

    def prep_outputs(
        self,
        inputs: dict[str, str],
        outputs: dict[str, str],
        return_only_outputs: bool = False,
    ) -> dict[str, str]:
        """Remove the mermory persistence part."""
        self._validate_outputs(outputs)
        # sometimes LLM wrap summarization in quotes
        outputs[self.output_key] = outputs[self.output_key].strip('"')
        if return_only_outputs:
            return outputs
        else:
            return {**inputs, **outputs}
