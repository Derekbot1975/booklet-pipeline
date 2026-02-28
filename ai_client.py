"""
Shared Anthropic client helper with streaming support.

The Anthropic SDK requires streaming for requests that may take >10 minutes.
This module provides a drop-in replacement that uses streaming internally
but returns the same response shape as messages.create().
"""

import logging
import os

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Return a shared Anthropic client instance."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


class StreamedResponse:
    """Mimics the shape of a non-streamed Messages response."""
    def __init__(self, text, stop_reason, usage):
        self.content = [type("Block", (), {"text": text})]
        self.stop_reason = stop_reason
        self.usage = usage


def create_message(*, model, max_tokens, system, messages, **kwargs):
    """Create a message using streaming to avoid the 10-minute timeout.

    Returns a response object with the same interface as client.messages.create():
      - response.content[0].text
      - response.stop_reason
      - response.usage.input_tokens / .output_tokens
    """
    client = get_client()

    chunks = []
    stop_reason = None
    input_tokens = 0
    output_tokens = 0

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system if isinstance(system, list) else [{"type": "text", "text": system}],
        messages=messages,
        **kwargs,
    ) as stream:
        for event in stream:
            # Collect text deltas
            if hasattr(event, 'type'):
                if event.type == 'content_block_delta' and hasattr(event, 'delta'):
                    if hasattr(event.delta, 'text'):
                        chunks.append(event.delta.text)
                elif event.type == 'message_delta' and hasattr(event, 'delta'):
                    if hasattr(event.delta, 'stop_reason'):
                        stop_reason = event.delta.stop_reason
                    if hasattr(event, 'usage') and hasattr(event.usage, 'output_tokens'):
                        output_tokens = event.usage.output_tokens
                elif event.type == 'message_start' and hasattr(event, 'message'):
                    if hasattr(event.message, 'usage'):
                        input_tokens = event.message.usage.input_tokens

    full_text = ''.join(chunks)

    # Build a usage-like object
    usage = type("Usage", (), {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    })

    return StreamedResponse(
        text=full_text,
        stop_reason=stop_reason or "end_turn",
        usage=usage,
    )
