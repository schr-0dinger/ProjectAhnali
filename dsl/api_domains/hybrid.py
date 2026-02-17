"""
Hybrid/reactive-domain DSL surface.

The default app mode remains static. Reactive APIs are opt-in via:
`app_config(mode="reactive")`.
"""

from dsl.api import (
    app_config,
    bind_text,
    derived,
    listen,
    observable,
    observable_get,
    reactive_bind_text,
    reactive_derived,
    reactive_get,
    reactive_listen,
    reactive_observable,
    reactive_set,
    set_observable,
)

HYBRID_API_STATUS = "guardrail_v0"

__all__ = [
    "HYBRID_API_STATUS",
    "app_config",
    "observable",
    "reactive_observable",
    "set_observable",
    "reactive_set",
    "observable_get",
    "reactive_get",
    "derived",
    "reactive_derived",
    "listen",
    "reactive_listen",
    "bind_text",
    "reactive_bind_text",
]
