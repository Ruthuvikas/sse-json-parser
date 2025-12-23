# SSE JSON Parser

A lightweight Python library for parsing Server-Sent Events (SSE) streams and extracting JSON payloads. Designed to work seamlessly with `boto3` event streams.

## Installation

```bash
pip install sse-json-parser
```

## Usage

### Basic Usage

```python
from sse_json_parser import SSEParser

# distinct chunks of bytes
stream = [b'data: {"foo": "bar"}\n\n', b'data: {"baz": "qux"}\n\n']
parser = SSEParser()

for event in parser.parse(stream):
    print(event)
# Output:
# {'foo': 'bar'}
# {'baz': 'qux'}
```

### With Boto3

```python
import boto3
from sse_json_parser import SSEParser, BotoStreamAdapter

client = boto3.client('bedrock-runtime') # Example service
response = client.invoke_model_with_response_stream(...)

adapter = BotoStreamAdapter(response['body'])
parser = SSEParser()

for event in parser.parse(adapter):
    print(event)
```
