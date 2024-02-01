from typing import Dict, Any

class SessionContext:
    """Class to manage session-specific context for AutoGen Studio."""

    def __init__(self):
        self._context_store: Dict[str, Any] = {}

    def set_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Set the context for a given session ID."""
        self._context_store[session_id] = context

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get the context for a given session ID."""
        return self._context_store.get(session_id, {})

    def clear_context(self, session_id: str) -> None:
        """Clear the context for a given session ID."""
        if session_id in self._context_store:
            del self._context_store[session_id]
