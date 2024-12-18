import unittest

from chatbot.embeddings.huggingface import BaseHuggingfaceTEI


class TestBaseHuggingfaceTEI(unittest.TestCase):
    class BaseHuggingfaceTEIStub(BaseHuggingfaceTEI):
        # Stub class to test _split_inputs
        @property
        def model(self) -> str:
            return "stub_model"

    def setUp(self):
        # Create an instance with a small batch_size for testing
        self.obj = self.BaseHuggingfaceTEIStub(
            base_url="http://example.com", batch_size=3
        )

    def test_split_inputs_exact_batch_size(self):
        inputs = ["input1", "input2", "input3"]
        result = self.obj._split_inputs(inputs)
        expected_result = [["input1", "input2", "input3"]]
        self.assertEqual(result, expected_result)

    def test_split_inputs_partial_batch(self):
        inputs = ["input1", "input2", "input3", "input4"]
        result = self.obj._split_inputs(inputs)
        expected_result = [["input1", "input2", "input3"], ["input4"]]
        self.assertEqual(result, expected_result)

    def test_split_inputs_multiple_batches(self):
        inputs = ["input1", "input2", "input3", "input4", "input5", "input6"]
        result = self.obj._split_inputs(inputs)
        expected_result = [
            ["input1", "input2", "input3"],
            ["input4", "input5", "input6"],
        ]
        self.assertEqual(result, expected_result)

    def test_split_inputs_single_input(self):
        inputs = ["input1"]
        result = self.obj._split_inputs(inputs)
        expected_result = [["input1"]]
        self.assertEqual(result, expected_result)

    def test_split_inputs_empty(self):
        inputs = []
        result = self.obj._split_inputs(inputs)
        expected_result = []
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
