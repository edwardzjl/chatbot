"""
<https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py>
<https://huggingface.co/internlm/internlm-chat-7b-8k/blob/bd546fa984b4b0b86958f56bf37f94aa75ab8831/modeling_internlm.py#L771>
"""

from langchain.prompts import PromptTemplate


human_prefix = "<|User|>"
ai_prefix = "<|Bot|>"
human_suffix = "<eoh>"
ai_suffix = "<eoa>"

template = f"""A chat between a curious <|User|> and an <|Bot|>. The <|Bot|> gives helpful, detailed, and polite answers to the <|User|>'s questions.


{{history}}
<s>{human_prefix}:{{input}}{human_suffix}
{ai_prefix}:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)
