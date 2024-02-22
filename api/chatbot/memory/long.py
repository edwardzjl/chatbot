from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import BaseMessage


class LongTermHistory(SQLChatMessageHistory):

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in db"""
        super().add_message(message)
        # TODO: add the message (id) to vector store
        self.embed(message)

    def embed(self, message: BaseMessage) -> None:
        """Append the message to the record in db"""
        with self.Session() as session:
            session.add(self.converter.to_sql_model(message, self.session_id))
            session.commit()
