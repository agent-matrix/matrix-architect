"""Distributed tracing support"""

import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable for trace ID
_trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


class Tracer:
    """Simple tracer for distributed tracing"""

    @staticmethod
    def start_trace(trace_id: Optional[str] = None) -> str:
        """Start a new trace"""
        if not trace_id:
            trace_id = str(uuid.uuid4())

        _trace_id.set(trace_id)
        return trace_id

    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get current trace ID"""
        return _trace_id.get()

    @staticmethod
    def clear_trace():
        """Clear trace context"""
        _trace_id.set(None)
