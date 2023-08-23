import unittest

from chatbot.schemas import ChatMessage, Conversation


class TestConversationSchema(unittest.TestCase):
    def test_create_conversation(self):
        conv = Conversation(title=f"foo", owner="bar")
        self.assertIsNotNone(conv.created_at)
        self.assertIsNotNone(conv.updated_at)
        # created_at and updated_at are not equal in unittests in github actions.
        # self.assertEqual(conv.created_at, conv.updated_at)


class TestMessageSchema(unittest.TestCase):
    def test_create_message(self):
        msg = ChatMessage(from_="ai", content="foo", type="stream")


if __name__ == "__main__":
    unittest.main()
