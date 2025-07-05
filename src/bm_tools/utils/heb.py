"""Hebrew word utility functions."""


def constanants(text: str) -> str:
    """Return a string containing only hebrew consanants."""
    return "".join([char for char in text if "א" <= char <= "ת"])
