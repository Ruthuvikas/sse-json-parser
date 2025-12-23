import os
import sys
import json
import time

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, it might still work if env var is set manually
    pass

# Check imports
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
except ImportError:
    print("Please install dependencies: pip install langgraph langchain-openai")
    sys.exit(1)

from sse_json_parser import SSEParser

def mock_sse_generator(agent_stream):
    """
    Takes a LangGraph/LangChain stream and yields it as raw SSE bytes.
    This simulates what reading from a network socket would look like.
    """
    for chunk in agent_stream:
        # LangChain chunks are objects, we need to serialize them
        # In a real app, the server would serialize the whole object or just content
        if hasattr(chunk, 'content'):
            payload = {'content': chunk.content, 'type': 'token'}
        else:
            payload = {'data': str(chunk), 'type': 'raw'}
            
        # Format as SSE
        # data: {"content": "...", "type": "token"}\n\n
        json_payload = json.dumps(payload)
        sse_string = f"data: {json_payload}\n\n"
        
        # Yield bytes (simulating network)
        yield sse_string.encode('utf-8')
        
        # Simulate slight network delay
        time.sleep(0.02)

def main():
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please export it: export OPENAI_API_KEY=sk-...")
        return

    print("--- LangGraph + SSE Parser Demo ---")
    print("Initializing ChatOpenAI...")
    
    model = ChatOpenAI(model="gpt-3.5-turbo", streaming=True)
    
    # Request a longer response to demonstrate sustained streaming
    prompt = "Write a 300-word short story about a robot learning to paint."
    messages = [HumanMessage(content=prompt)]
    
    print(f"\nStreaming response for: '{prompt}'\n")
    print("-" * 40)

    # 1. Get the raw object stream from LangChain
    raw_stream = model.stream(messages)
    
    # 2. "Network Simulation": Convert objects -> SSE Bytes
    sse_byte_stream = mock_sse_generator(raw_stream)
    
    # 3. Parse back with our library
    parser = SSEParser()
    
    collected_text = ""
    
    for event in parser.parse(sse_byte_stream):
        # parser.parse yields the dict we serialized in mock_sse_generator
        if 'content' in event:
            token = event['content']
            collected_text += token
            # Stream to stdout
            sys.stdout.write(token)
            sys.stdout.flush()
            
    print("\n" + "-" * 40)
    print("\nDone!")

if __name__ == "__main__":
    main()
