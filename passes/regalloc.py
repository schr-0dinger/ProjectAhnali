# passes/regalloc.py
#
# Public register allocation interface.
# Re-exports the active allocator so callers don't need to know
# which algorithm is behind it. Swap the import here to change
# the allocator without touching every downstream caller.

from passes.regalloc_linear import LinearScanAllocator as RegisterAllocator
from passes.regalloc_linear import LiveInterval

__all__ = ["RegisterAllocator", "LiveInterval"]
