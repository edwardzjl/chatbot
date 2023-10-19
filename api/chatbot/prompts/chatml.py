"""Prompt template for OpenAI's Chat Markup Language, or ChatML.
See <https://github.com/openai/openai-python/blob/main/chatml.md> for more details."""

from langchain import PromptTemplate


human_prefix = "<|im_start|>user"
ai_prefix = "<|im_start|>assistant"
human_suffix = "<|im_end|>"
ai_suffix = "<|im_end|>"

template = """<|im_start|>system
You are Mistral-OpenOrca, a large language model trained by Open-Orca. Answer as concisely as possible.
Knowledge cutoff: 2023-10-01
Current date: {{date}}<|im_end|>

{{history}}
{human_prefix}
{{input}}{human_suffix}
{ai_prefix}
"""

prompt = PromptTemplate(
    input_variables=["history", "input", "date"],
    template=template.format(
        human_prefix=human_prefix, human_suffix=human_suffix, ai_prefix=ai_prefix
    ),
)
