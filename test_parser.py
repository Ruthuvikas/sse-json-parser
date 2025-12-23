import unittest
from sse_json_parser import SSEParser

class TestSSEParser(unittest.TestCase):
    def test_simple_event(self):
        chunks = [b'data: {"foo": "bar"}\n\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        self.assertEqual(results, [{"foo": "bar"}])

    def test_split_event(self):
        chunks = [b'data: {"fo', b'o": "bar"}\n\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        self.assertEqual(results, [{"foo": "bar"}])
    
    def test_split_delimiter(self):
        chunks = [b'data: {"foo": "bar"}\n', b'\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        self.assertEqual(results, [{"foo": "bar"}])

    def test_multiple_events_single_chunk(self):
        chunks = [b'data: {"a": 1}\n\ndata: {"b": 2}\n\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        self.assertEqual(results, [{"a": 1}, {"b": 2}])
    
    def test_multiline_data(self):
        # Spec says newline in data is just concatenation with newline
        chunks = [b'data: {"a":\n', b'data: 1}\n\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        # This effectively becomes `{"a":\n1}` which is valid JSON
        self.assertEqual(results, [{"a": 1}])
    
    def test_invalid_json_ignored(self):
        chunks = [b'data: invalid\n\n', b'data: {"valid": true}\n\n']
        parser = SSEParser()
        results = list(parser.parse(chunks))
        # The invalid one is skipped
        self.assertEqual(results, [{"valid": True}])

if __name__ == '__main__':
    unittest.main()
