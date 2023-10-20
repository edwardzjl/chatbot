from langchain.prompts import PromptTemplate

human_prefix = " <reserved_102> "
ai_prefix = " <reserved_103> "
human_suffix = None
ai_suffix = "</s>"

template = f"""{{history}}
{human_prefix}: {{input}}
{ai_prefix}:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)
