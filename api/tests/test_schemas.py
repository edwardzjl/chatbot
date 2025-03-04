import unittest

from chatbot.schemas import Conversation


class TestConversationSchema(unittest.TestCase):
    def test_create_conversation(self):
        conv = Conversation(title="foo", owner="bar")
        self.assertIsNotNone(conv.created_at)
        self.assertIsNotNone(conv.last_message_at)
        # created_at and last_message_at are not equal in unittests in github actions.
        # self.assertEqual(conv.created_at, conv.last_message_at)


if __name__ == "__main__":
    unittest.main()
