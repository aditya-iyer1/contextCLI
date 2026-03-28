"""
Controlled synthetic extractive-QA corpus for SIG-02 (Alpha).

Needle-offset is the primary difficulty knob: higher bins bury the answer deeper in the
context by lengthening prefix filler. Filler is secondary—only to realize length and
burial schedules aligned with `.planning/DATASET-SIG02.md`.
"""

from __future__ import annotations

import tiktoken

from contextcliff.data.formats import Example

ALPHA_SIG02_SEED = 42
SYNTHETIC_VERSION = "sig02-v1"
N_PER_BIN_DEFAULT = 10

_LOREM = " lorem "


def _get_encoder():
    try:
        return tiktoken.get_encoding("o200k_base")
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def build_alpha_synthetic_examples(n_bins: int, n_per_bin: int, seed: int) -> list[Example]:
    """
    Build `n_bins` designed strata with `n_per_bin` examples each (equal n per bin).

    Prefix filler length scales with `bin_index` so `context_tokens` minima increase
    strictly by bin. The answer appears once between <<< and >>> in the needle line.
    """
    _ = seed  # reserved for future stochastic filler; construction is deterministic given args
    enc = _get_encoder()
    examples: list[Example] = []

    question = (
        "What is the exact answer string between the markers <<< and >>> ?"
    )

    for bin_index in range(1, n_bins + 1):
        for j in range(n_per_bin):
            answer = f"asig02_{bin_index:02d}_{j:02d}_answer"
            # Prefix grows with bin_index (primary) and j (minor spread within bin).
            prefix_repeats = 120 * bin_index + j
            prefix = _LOREM * prefix_repeats
            needle_line = f"Needle: <<<{answer}>>>"
            context = prefix + "\n" + needle_line

            needle_offset = context.find(answer)
            if needle_offset < 0:
                raise RuntimeError(f"answer not found in context: {answer!r}")

            context_tokens = len(enc.encode(context))
            ex_id = f"alpha_sig02_{bin_index:02d}_{j:03d}"
            metadata = {
                "synthetic_version": SYNTHETIC_VERSION,
                "alpha_bin": bin_index,
                "needle_offset": needle_offset,
            }
            examples.append(
                Example(
                    id=ex_id,
                    context=context,
                    question=question,
                    answers=[answer],
                    context_tokens=context_tokens,
                    metadata=metadata,
                )
            )

    # Monotonicity: min context_tokens per bin strictly increases with bin_index.
    by_bin: dict[int, list[Example]] = {}
    for ex in examples:
        b = ex.metadata["alpha_bin"]
        by_bin.setdefault(b, []).append(ex)
    for b in range(1, n_bins):
        min_b = min(x.context_tokens for x in by_bin[b])
        min_next = min(x.context_tokens for x in by_bin[b + 1])
        assert min_b < min_next, (b, min_b, min_next)

    return examples
