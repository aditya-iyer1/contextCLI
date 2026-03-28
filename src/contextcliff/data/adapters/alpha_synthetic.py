"""Adapter for SIG-02 `alpha_synthetic` controlled corpus (generator-backed, finite stream)."""

from typing import Iterator

from contextcliff.data.adapters.base import BaseAdapter
from contextcliff.data.alpha_synthetic_generator import build_alpha_synthetic_examples
from contextcliff.data.formats import Example


class AlphaSyntheticAdapter(BaseAdapter):
    """Finite stream over pre-built synthetic examples (designed bins, not quantiles)."""

    def __init__(self, n_bins: int, n_per_bin: int, seed: int):
        self._examples = build_alpha_synthetic_examples(n_bins, n_per_bin, seed)

    def load_stream(self) -> Iterator[Example]:
        yield from iter(self._examples)
