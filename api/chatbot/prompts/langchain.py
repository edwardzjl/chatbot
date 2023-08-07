from langchain.prompts import PromptTemplate

template = """The following is a friendly conversation between a human and an AI assistant. The Assistant is talkative and provides lots of specific details from its context. If the Assistant does not know the answer to a question, it truthfully says it does not know.

Current conversation:
{history}
Human: {input}
Assistant:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

human_prefix = "Human"
ai_prefix = "Assistant"
human_suffix = None
ai_suffix = None
