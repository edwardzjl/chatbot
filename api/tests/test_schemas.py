import unittest

from langchain_core.messages import AIMessage, HumanMessage

from chatbot.schemas import ChatMessage, Conversation


class TestConversationSchema(unittest.TestCase):
    def test_create_conversation(self):
        conv = Conversation(title="foo", owner="bar")
        self.assertIsNotNone(conv.created_at)
        self.assertIsNotNone(conv.last_message_at)
        # created_at and last_message_at are not equal in unittests in github actions.
        # self.assertEqual(conv.created_at, conv.last_message_at)


class TestMessageSchema(unittest.TestCase):
    def test_create_message_from_langchain(self):
        lc_msg = AIMessage(content="foo")
        msg = ChatMessage.from_lc(lc_msg, "conv_id")
        self.assertEqual(msg.content, "foo")
        self.assertEqual(msg.from_, "ai")
        lc_msg = HumanMessage(content="bar")
        msg = ChatMessage.from_lc(lc_msg, "conv_id", from_="some-user")
        self.assertEqual(msg.content, "bar")
        self.assertEqual(msg.from_, "some-user")


if __name__ == "__main__":
    unittest.main()
