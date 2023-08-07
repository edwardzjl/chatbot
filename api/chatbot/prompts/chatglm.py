from langchain.prompts import PromptTemplate

template = """{history}
问: {input}
答:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

human_prefix = "问"
ai_prefix = "答"
human_suffix = None
ai_suffix = None
