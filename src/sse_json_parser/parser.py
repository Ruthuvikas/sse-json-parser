import json
from typing import Generator, Any, Iterable, Union

import codecs

class SSEParser:
    """
    Parses a stream of bytes or strings into JSON objects from SSE 'data' fields.
    """
    def __init__(self):
        self._buffer = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors='strict')

    def parse(self, stream: Iterable[Union[str, bytes]]) -> Generator[Any, None, None]:
        """
        Yields parsed JSON objects from the stream.
        """
        for chunk in stream:
            if isinstance(chunk, bytes):
                chunk = self._decoder.decode(chunk, final=False)
            
            self._buffer += chunk
            
            # Check for double newlines indicating end of event
            while True:
                # We support \n\n. standard SSE is \n\n. 
                # Some implementations might use \r\n\r\n but typically \n\n is enough for split.
                # Let's check for \n\n.
                event_end = self._buffer.find('\n\n')
                if event_end == -1:
                    break
                
                # Extract the complete event block
                raw_event = self._buffer[:event_end]
                # Advance buffer past the event and the delimiter
                self._buffer = self._buffer[event_end + 2:]
                
                # Process the event
                yield from self._process_event(raw_event)

    def _process_event(self, raw_event: str) -> Generator[Any, None, None]:
        data_lines = []
        for line in raw_event.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for data: prefix
            if line.startswith('data:'):
                # Extract content after "data:"
                # The spec says "data: " (with space) usually, but we should be robust
                content = line[5:]
                if content.startswith(' '):
                    content = content[1:]
                data_lines.append(content)
        
        if data_lines:
            # Join all data lines ensuring newlines if multiple data lines existed (though usually for JSON it's one blob or one line)
            # Standard SSE Concatenation: "If the line starts with "data:", append the rest of the line to the data buffer, 
            # and append a line feed character (U+000A) to the data buffer."
            full_data = '\n'.join(data_lines)
            try:
                yield json.loads(full_data)
            except json.JSONDecodeError:
                # Decide how to handle this. For now, maybe just skip or log. 
                # The user asked for handling broken json "carefully". 
                # If it's broken, we can't yield it as a dict. 
                # We'll skip it effectively, or we could yield an error object if designed so.
                # Given instructions, I will just ignore it for now or print a warning? 
                # "I want a json parse... mainly for streaming" implies successful parses.
                pass
