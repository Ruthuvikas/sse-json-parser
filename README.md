# SSE JSON Parser

A lightweight, robust Python library for parsing Server-Sent Events (SSE) streams and extracting JSON payloads.

Designed for resilience, it handles:
- **Network Fragmentation**: Correctly parses events split across multiple byte chunks.
- **Multi-byte Characters**: Handles UTF-8 characters (like emojis ☃️) split across chunks.
- **Boto3 Integration**: Native support for AWS SDK streams (e.g., Bedrock).
- **LangChain/LangGraph**: Easy integration with AI agent streams.

**Zero dependencies.**

## Installation

```bash
pip install sse-json-parser
```
*(Or install locally: `pip install .`)*

## Usage

### 1. Basic Usage

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

### 2. With AWS Boto3 (Bedrock)

Ideal for consuming streaming responses from AWS Bedrock or other AWS services.

```python
import boto3
from sse_json_parser import SSEParser, BotoStreamAdapter

client = boto3.client('bedrock-runtime') 
response = client.invoke_model_with_response_stream(...)

# Adapter handles the specific Boto3 EventStream structure
adapter = BotoStreamAdapter(response['body'])
parser = SSEParser()

for event in parser.parse(adapter):
    print(event)
```

### 3. With LangGraph / LangChain

Easily consume streams from LangChain agents.

```python
import sys
from sse_json_parser import SSEParser

# Assuming you have a stream of bytes (e.g., from an SSE endpoint)
# If communicating within Python, normally you use objects, but this library 
# is for when you are consuming the raw SSE network stream.

parser = SSEParser()
for event in parser.parse(sse_byte_stream):
    if 'content' in event:
        sys.stdout.write(event['content'])
```

## Development

### Running Tests
```bash
python3 -m unittest discover
```

### Running Examples
See `langgraph_agent.py` for a full end-to-end example with OpenAI.
```bash
python3 langgraph_agent.py
```
