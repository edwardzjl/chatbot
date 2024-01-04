from langchain.chains import LLMChain
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from langchain_core.prompts import PromptTemplate

_prompt = """<|im_start|>system
You are Rei, the ideal assistant dedicated to assisting users effectively.<|im_end|>
{history}
<|im_start|>system
Now Provide a short title of the conversation in less than 10 words.<|im_end|>
<|im_start|>assistant
"""
prompt = PromptTemplate(
    input_variables=["history"],
    template=_prompt,
)


class SummarizationChain(LLMChain):
    def prep_outputs(
        self,
        inputs: dict[str, str],
        outputs: dict[str, str],
        return_only_outputs: bool = False,
    ) -> dict[str, str]:
        """Remove the mermory persistence part."""
        self._validate_outputs(outputs)
        if return_only_outputs:
            return outputs
        else:
            return {**inputs, **outputs}


async def summarize(
    llm: BaseLLM,
    memory: BaseMemory,
) -> str:
    external_context = memory.load_memory_variables({})
    chain = SummarizationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=False,
    )
    res = await chain.acall(inputs=external_context)
    # sometimes LLM wrap summarization in quotes
    return res["text"].strip('"')
