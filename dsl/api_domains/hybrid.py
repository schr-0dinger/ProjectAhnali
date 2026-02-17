"""
Hybrid-domain DSL surface placeholder.

The v1 static-first runtime keeps hybrid APIs gated behind explicit
Milestone D/E work. This module exists to reserve a stable import path:
`dsl.api_domains.hybrid`.
"""

HYBRID_API_STATUS = "planned"

__all__ = ["HYBRID_API_STATUS"]
