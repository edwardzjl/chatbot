from langchain.prompts import PromptTemplate

template = """
{history}
<s><|User|>:{input}<eoh>
<|Bot|>:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

human_prefix = "<|User|>"
ai_prefix = "<|Bot|>"
human_suffix = "<eoh>"
ai_suffix = "<eoa>"
