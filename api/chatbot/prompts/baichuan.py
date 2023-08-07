from langchain.prompts import PromptTemplate

template = """{history}
 <reserved_102> : {input}
 <reserved_103> :"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

human_prefix = " <reserved_102> "
ai_prefix = " <reserved_103> "
human_suffix = None
ai_suffix = "</s>"
