"""Common error types."""

from collections.abc import Iterable

__all__ = ("InvalidOptionError",)


class InvalidOptionError(BaseException):
    """Value is not one of the valid options."""

    def __init__(self, name: str, options: Iterable, value: object) -> None:
        """Initialise error.

        Args:
           name: the name of the option for the error message
           options: iterable of the option strings
           value: the invalid object received
        """
        super().__init__(f"{name} '{value}' is not one of the options: {options}")
