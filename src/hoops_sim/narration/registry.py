"""Generic registry for narration components.

Provides a type-safe, decorator-based registration pattern so that
new sequence recognizers, clause generators, voice profiles, etc.
can be added without modifying core pipeline code.
"""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Generic registry for narration components."""

    def __init__(self, name: str = "") -> None:
        self.name = name
        self._entries: dict[str, T] = {}

    def register(self, key: str) -> Callable:
        """Decorator to register a component under *key*."""

        def decorator(cls: T) -> T:
            self._entries[key] = cls
            return cls

        return decorator

    def register_instance(self, key: str, instance: T) -> None:
        """Register an already-instantiated component."""
        self._entries[key] = instance

    def get(self, key: str) -> T:
        """Retrieve a registered component by key."""
        if key not in self._entries:
            raise KeyError(
                f"Registry '{self.name}': no entry for key '{key}'. "
                f"Available: {list(self._entries.keys())}"
            )
        return self._entries[key]

    def get_or_none(self, key: str) -> T | None:
        """Retrieve a registered component or None."""
        return self._entries.get(key)

    def keys(self) -> list[str]:
        """Return all registered keys."""
        return list(self._entries.keys())

    def override(self, key: str, impl: T) -> None:
        """Override an existing registration (for testing/hacking)."""
        self._entries[key] = impl

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __len__(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Global registry instances
# ---------------------------------------------------------------------------

sequence_registry: Registry = Registry("sequence_recognizers")
clause_generator_registry: Registry = Registry("clause_generators")
voice_profile_registry: Registry = Registry("voice_profiles")
