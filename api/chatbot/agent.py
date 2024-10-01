from datetime import date

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.graph import CompiledGraph


def create_agent(
    chat_model: BaseChatModel, checkpointer: BaseCheckpointSaver
) -> CompiledGraph:
    async def chatbot(state: MessagesState) -> MessagesState:
        """Process the current state and generate a response using the LLM."""

        instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively.
    Knowledge cutoff: 2023-10-01
    Current date: {date}
    Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instruction),
                ("placeholder", "{messages}"),
            ]
        )

        bound = prompt | chat_model

        windowed_messages = trim_messages(
            state["messages"],
            token_counter=len,
            max_tokens=20,
            start_on="human",  # This means that the first message should be from the user after trimming.
        )

        messages = await bound.ainvoke(
            {
                "messages": windowed_messages,
                "date": date.today(),  # TODO: maybe cannot get date here.
            }
        )
        return {
            "messages": [messages],
        }

    builder = StateGraph(MessagesState)
    builder.add_node(chatbot)

    # Add edges to the graph
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    # Compile the graph
    graph = builder.compile(checkpointer=checkpointer)
    return graph
