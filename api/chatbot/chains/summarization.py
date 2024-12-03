from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def create_smry_chain(chat_model):
    instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively."""

    tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("placeholder", "{messages}"),
            (
                "system",
                "Now Provide a short summarization for the above messages in less than 10 words, using the same language as the user.",
            ),
        ]
    )

    return tmpl | chat_model | StrOutputParser()
