# SSE JSON Parser

A lightweight, robust Python library for parsing Server-Sent Events (SSE) streams, specifically optimized for **AI Agents** and **LLM Streaming**.

## Why use this for Agents?

When building AI Agents (using LangChain, LangGraph, or AWS Bedrock), responses are often streamed to the client to reduce latency (Time to First Byte). 

However, these streams are often **fragmented** when they travel over the network. A single JSON object representing a token or a tool call might be split across multiple chunks:

```text
Chunk 1: data: {"type": "content_
Chunk 2: block_delta", "delta": {"text": "Hello W
Chunk 3: orld"}}
```

A standard JSON parser will fail on `Chunk 1`. `sse-json-parser` buffers these chunks and only yields when a complete, valid JSON event is available.

It handles:
- **Token Streaming**: reconstructing split text deltas.
- **Tool Calls**: buffering large tool input JSONs until they are complete.
- **Multi-byte Characters**: correctly handling emojis or unicode characters split across chunks.

## Installation

```bash
pip install sse-json-parser
```
*(Or install locally: `pip install .`)*

## Usage

### 1. With LangGraph / LangChain (Agent Streaming)

This is the primary use case. If you are serving a LangGraph agent via a streaming endpoint (like FastAPI), the client needs to reconstruct the events.

```python
import sys
from sse_json_parser import SSEParser

# 'sse_byte_stream' is your network response iterator (e.g. requests.iter_content)
parser = SSEParser()

print("Agent Response:")
for event in parser.parse(sse_byte_stream):
    # 'event' is a fully parsed dict
    if event.get('type') == 'token':
        # Print tokens in real-time as a typewriter effect
        sys.stdout.write(event['content'])
        sys.stdout.flush()
        
    elif event.get('type') == 'tool_use':
        print(f"\n[Agent is using tool: {event['name']}]")
```

### 2. With AWS Boto3 (Amazon Bedrock)

Ideal for consuming streaming responses from AWS Bedrock, which often sends split JSON frames.

```python
import boto3
from sse_json_parser import SSEParser, BotoStreamAdapter

client = boto3.client('bedrock-runtime') 
response = client.invoke_model_with_response_stream(...)

# Adapter handles the specific Boto3 EventStream structure automatically
adapter = BotoStreamAdapter(response['body'])
parser = SSEParser()

for event in parser.parse(adapter):
    # 'event' is the dictionary returned by the API
    if 'chunk' in event:
         print(event['chunk'].get('bytes', b''), end='')
    elif 'completion' in event:
         print(event['completion'], end='')
```

### 3. Basic Usage

```python
from sse_json_parser import SSEParser

stream = [b'data: {"foo": "bar"}\n\n', b'data: {"baz": "qux"}\n\n']
parser = SSEParser()

for event in parser.parse(stream):
    print(event)
```

## Development

- **Run Tests**: `python3 -m unittest discover`
- **Agent Demo**: See `langgraph_agent.py` for a full OpenAI integration example.
