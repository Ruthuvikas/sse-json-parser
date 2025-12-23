import unittest
from unittest.mock import MagicMock
from sse_json_parser import BotoStreamAdapter

class TestBotoStreamAdapter(unittest.TestCase):
    def test_streaming_body_iter_chunks(self):
        mock_stream = MagicMock()
        mock_stream.iter_chunks.return_value = iter([b'chunk1', b'chunk2'])
        # Ensure it doesn't look like an EventStream
        del mock_stream.__iter__ 
        
        adapter = BotoStreamAdapter(mock_stream)
        results = list(adapter)
        self.assertEqual(results, [b'chunk1', b'chunk2'])

    def test_event_stream_chunk(self):
        # Mocking an iterable EventStream
        mock_stream = [
            {'chunk': {'bytes': b'event1'}},
            {'chunk': {'bytes': b'event2'}}
        ]
        adapter = BotoStreamAdapter(mock_stream)
        results = list(adapter)
        self.assertEqual(results, [b'event1', b'event2'])

    def test_event_stream_payload(self):
        mock_stream = [
            {'payload': b'payload1'},
            {'payload': b'payload2'}
        ]
        adapter = BotoStreamAdapter(mock_stream)
        results = list(adapter)
        self.assertEqual(results, [b'payload1', b'payload2'])

if __name__ == '__main__':
    unittest.main()
