"""Templates for bible modules."""

from jinja2 import (
    Environment,
    PackageLoader,
    StrictUndefined,
    Template,
    select_autoescape,
)

__all__ = ("get_template",)


def _get_environment() -> Environment:
    """Get the jinja2 environment."""
    return getattr(
        _get_environment,
        "environment",
        Environment(
            loader=PackageLoader("abm_tools"),
            undefined=StrictUndefined,
            autoescape=select_autoescape(),
        ),
    )


def get_template(name: str) -> Template:
    """Get a template by name."""
    env = _get_environment()

    return env.get_template(name)
