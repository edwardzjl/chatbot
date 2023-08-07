from langchain.prompts import PromptTemplate

template = """A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.

{history}
USER: {input}
ASSISTANT:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)

human_prefix = "USER"
ai_prefix = "ASSISTANT"
human_suffix = None
ai_suffix = "</s>"
