from typing import Iterable, Union, Any

class BotoStreamAdapter:
    """
    Adapts a Boto3 EventStream or StreamingBody to a simple iterable of bytes.
    """
    def __init__(self, raw_stream: Any):
        self.raw_stream = raw_stream

    def __iter__(self) -> Iterable[bytes]:
        # Handle StreamingBody (e.g. from S3 get_object or invoke_model generic)
        if hasattr(self.raw_stream, 'iter_chunks'):
            yield from self.raw_stream.iter_chunks()
        
        # Handle EventStream (e.g. from invoke_model_with_response_stream)
        # Boto3 EventStream objects are iterables that yield events. 
        # Each event is a dict. We usually want the 'bytes' from the 'chunk' key 
        # or the payload key depending on the service.
        # This is a bit generic, specific services like Bedrock have specific structure `{'chunk': {'bytes': b'...'}}`
        elif hasattr(self.raw_stream, '__iter__'):
             for event in self.raw_stream:
                # Bedrock/typical structure
                if 'chunk' in event:
                    yield event['chunk'].get('bytes', b'')
                elif 'payload' in event: 
                    # Some other services might use payload
                    yield event['payload']
                elif isinstance(event, bytes):
                    yield event
                # Add more heuristics as needed
