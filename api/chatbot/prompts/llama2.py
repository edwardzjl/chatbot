"""
<https://huggingface.co/TheBloke/Llama-2-13B-chat-GPTQ/discussions/5>
<https://github.com/facebookresearch/llama/blob/6c7fe276574e78057f917549435a2554000a876d/llama/generation.py#L213>
"""

from langchain.prompts import PromptTemplate

human_prefix = ""
ai_prefix = ""
human_suffix = " [/INST]"
ai_suffix = " </s><s>[INST]"

# TODO: there will be a whitespace before the first user message that I cannot elegantly remove now.
template = f"""<s>[INST] <<SYS>>
{{system_message}}
<</SYS>>

{{history}} {{input}}{human_suffix}"""

prompt = PromptTemplate(
    input_variables=["system_message", "history", "input"], template=template
)
