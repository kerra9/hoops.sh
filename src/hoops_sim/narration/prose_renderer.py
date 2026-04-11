"""Layer 7: Prose Rendering.

Joins styled clauses into the final output string with correct
punctuation, spacing, and formatting. Enforces rhythm variation
at the sentence level.
"""

from __future__ import annotations

import re

from hoops_sim.narration.types import StyledClause


class DefaultProseRenderer:
    """Default implementation of the ProseRenderer protocol.

    Rendering rules:
    1. First clause: capitalize first letter, prepend subject
    2. Consecutive clauses from same subject at low intensity: comma flow
    3. Transition from low to high intensity: suspense (...)
    4. High intensity clauses: exclamation separation
    5. CAPS clauses: entire text uppercased
    6. Aftermath clauses: new sentence
    7. No double punctuation
    8. No orphan connectors at string boundaries
    """

    def render(self, clauses: list[StyledClause]) -> str:
        """Join styled clauses into the final prose string."""
        if not clauses:
            return ""

        parts: list[str] = []

        for i, clause in enumerate(clauses):
            text = clause.text
            if not text:
                continue

            if i == 0:
                # First clause: capitalize and add directly
                text = self._capitalize_first(text)
                parts.append(text)
            else:
                connector = clause.connector or " "
                parts.append(connector)
                parts.append(text)

            # Add terminal punctuation
            if clause.terminal:
                parts.append(clause.terminal)

        result = "".join(parts)

        # Post-processing cleanup
        result = self._cleanup(result)

        return result.strip()

    @staticmethod
    def _capitalize_first(text: str) -> str:
        """Capitalize the first character of text."""
        if not text:
            return text
        return text[0].upper() + text[1:]

    @staticmethod
    def _cleanup(text: str) -> str:
        """Clean up the rendered text."""
        # Remove double punctuation
        text = re.sub(r'([!.?])\1+', r'\1', text)
        # Remove orphan punctuation sequences like "!." or ".!"
        text = re.sub(r'!\.', '!', text)
        text = re.sub(r'\.!', '!', text)
        text = re.sub(r'\.\.\.\.\.*', '...', text)
        # Remove leading/trailing whitespace around punctuation
        text = re.sub(r'\s+([!.?,])', r'\1', text)
        # Remove double spaces
        text = re.sub(r'  +', ' ', text)
        # Remove orphan connectors at boundaries
        text = re.sub(r'^[\s,.\-!]+', '', text)
        text = re.sub(r'[\s,\-]+$', '', text)
        # Make sure the text ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        return text
