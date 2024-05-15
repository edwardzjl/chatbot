from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from chatbot.config import settings
from chatbot.memory import memory

instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively.
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""

tmpl = ChatPromptTemplate.from_messages(
    [
        ("system", instruction),
        MessagesPlaceholder(variable_name="history"),
        (
            "user",
            "Now Provide a short summarization of the conversation in less than 10 words.",
        ),
    ]
)

llm = ChatOpenAI(
    openai_api_base=str(settings.llm.url),
    model=settings.llm.model,
    openai_api_key=settings.llm.creds,
    max_tokens=1024,
    streaming=True,
)

smry_chain = (
    {
        "history": RunnableLambda(
            memory.load_memory_variables, afunc=memory.aload_memory_variables
        )
        | itemgetter("history")
    }
    | tmpl
    | llm
    | StrOutputParser()
)
