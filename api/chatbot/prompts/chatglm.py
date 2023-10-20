"""
<https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py>
"""

from langchain.prompts import PromptTemplate


human_prefix = "问"
ai_prefix = "答"
human_suffix = None
ai_suffix = None

template = f"""{{history}}
{human_prefix}: {{input}}
{ai_prefix}:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)
