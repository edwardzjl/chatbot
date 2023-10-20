"""Prompt template for OpenAI's Chat Markup Language, or ChatML.
See <https://github.com/openai/openai-python/blob/main/chatml.md> for more details."""

from langchain.prompts import PromptTemplate


human_prefix = "<|im_start|>user"
ai_prefix = "<|im_start|>assistant"
human_suffix = "<|im_end|>"
ai_suffix = "<|im_end|>"

template = f"""<|im_start|>system
{{system}}<|im_end|>

{{history}}
{human_prefix}
{{input}}{human_suffix}
{ai_prefix}
"""

prompt = PromptTemplate(
    input_variables=["system", "history", "input"],
    template=template,
)
