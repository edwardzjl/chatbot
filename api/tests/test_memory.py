import unittest

from chatbot.memory import FlexConversationBufferWindowMemory


class TestFlexConversationBufferWindowMemory(unittest.TestCase):
    def test_get_buffer_string_user_message(self):
        memo = FlexConversationBufferWindowMemory(
            human_prefix="<|im_start|>user",
            ai_prefix="<|im_start|>assistant",
            human_suffix="<|im_end|>",
            ai_suffix="<|im_end|>",
            prefix_delimiter="\n",
        )
        memo.chat_memory.add_user_message("Hello")
        buffer_str = """<|im_start|>user
Hello<|im_end|>"""
        self.assertEqual(memo.get_buffer_string(memo.chat_memory.messages), buffer_str)

    def test_get_buffer_string_ai_message(self):
        memo = FlexConversationBufferWindowMemory(
            human_prefix="<|im_start|>user",
            ai_prefix="<|im_start|>assistant",
            human_suffix="<|im_end|>",
            ai_suffix="<|im_end|>",
            prefix_delimiter="\n",
        )
        memo.chat_memory.add_ai_message("Hi")
        buffer_str = """<|im_start|>assistant
Hi<|im_end|>"""
        self.assertEqual(memo.get_buffer_string(memo.chat_memory.messages), buffer_str)


if __name__ == "__main__":
    unittest.main()
