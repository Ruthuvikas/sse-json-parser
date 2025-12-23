import time
import sys
# fake add to path
sys.path.append('src')

from sse_json_parser import SSEParser, BotoStreamAdapter

def mock_boto_stream():
    """
    Simulates a Boto3 EventStream yielding chunks of bytes.
    """
    events = [
        {'chunk': {'bytes': b'data: {"status": "start"}\n\n'}},
        {'chunk': {'bytes': b'data: {"token": "Hello"}\n\n'}},
        {'chunk': {'bytes': b'data: {"token": " World"}\n\n'}},
        {'chunk': {'bytes': b'data: {"status": "end"}\n\n'}},
    ]
    for event in events:
        time.sleep(0.1) # Simulate network delay
        yield event

def main():
    print("Starting stream simulation...")
    stream = mock_boto_stream()
    adapter = BotoStreamAdapter(stream)
    parser = SSEParser()

    for data in parser.parse(adapter):
        print(f"Received event: {data}")

if __name__ == "__main__":
    main()
