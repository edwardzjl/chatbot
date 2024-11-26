from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def create_smry_chain(chat_model):
    instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively.
    Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""

    tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("placeholder", "{messages}"),
            (
                "user",
                "Now Provide a short summarization for the above messages in less than 10 words.",
            ),
        ]
    )

    return tmpl | chat_model | StrOutputParser()
