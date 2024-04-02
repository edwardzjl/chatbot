from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively.
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""

tmpl = ChatPromptTemplate.from_messages(
    [
        ("system", instruction),
        MessagesPlaceholder(variable_name="history"),
        (
            "system",
            "Now Provide a short summarization of the conversation in less than 10 words.",
        ),
    ]
)
