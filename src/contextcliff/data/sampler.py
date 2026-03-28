
# Implements natural length distribution (NLDA) and verification detection (Wang, et al. 2026).
# Tokenizes a large buffer and pulls N samples per quantile

import json, random, time
import numpy as np
from dataclasses import asdict
from contextcliff.data.adapters.narrative_qa import NarrativeQAAdapter
from contextcliff.data.alpha_synthetic_generator import (
    ALPHA_SIG02_SEED,
    build_alpha_synthetic_examples,
)


def _write_alpha_synthetic_manifest(n_bins: int, n_per_bin: int, seed: int):
    """Write manifest.json from designed synthetic bins (SIG-02); returns examples."""
    examples = build_alpha_synthetic_examples(n_bins, n_per_bin, seed)
    manifest_data = [asdict(example) for example in examples]
    with open("manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Saved {len(examples)} samples to manifest.json (alpha_synthetic)")
    return examples


def balance_samples(
    n_per_bin: int = 10,
    buffer_size: int = 2000,
    dataset_name: str = "narrativeqa",
    *,
    n_bins: int = 10,
):
    """
    Loads and balances the samples in the dataset to ensure each bin has approximately the same number of samples.
    Merges sparse bins if needed (n < 10) to maintain statistical power.
    For ``alpha_synthetic``, ``n_bins`` is K (designed strata); for ``narrativeqa``, quantile bin count stays 10.
    """
    start_time = time.perf_counter()

    if dataset_name == "alpha_synthetic":
        examples = _write_alpha_synthetic_manifest(n_bins, n_per_bin, ALPHA_SIG02_SEED)
        elapsed_time = time.perf_counter() - start_time
        print(f"Time taken: {elapsed_time:.2f} seconds")
        return examples

    # 1. Initialize Adapter
    if dataset_name == "narrativeqa":
        adapter = NarrativeQAAdapter()
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    print(f"Streaming and tokenizing {buffer_size} samples from {dataset_name}...")
    examples = []
    
    # 2. Stream into buffer
    stream = adapter.load_stream()
    try:
        for i, example in enumerate(stream):
            if i >= buffer_size: break
            examples.append(example)
    except Exception as e:
        print(f"Stream interrupted or finished: {e}")

    print(f"Loaded {len(examples)} examples.")
    if not examples:
        print("No examples loaded.")
        return []

    # 3. Sort and Bin logic
    examples.sort(key=lambda x: x.context_tokens)
    lengths = [example.context_tokens for example in examples]
    
    if len(lengths) < 10:
        print("Not enough examples to quantize. Taking all.")
        selected_examples = examples
    else:
        # Calculate initial quantile edges (fixed 10-bin quantiles for narrativeqa)
        q_bins = 10
        edges = np.quantile(lengths, np.linspace(0, 1, q_bins + 1))  # 11 edges for 10 bins
        
        bins = [[] for _ in range(q_bins)]

        # Assign to bins
        for example in examples:
            # -1 because searchsorted returns 1 for the first bin (handling side='right' usually), 
            # actually side='right' on [0..10] edges:
            # if x < edge[0], index 0. if edge[0] <= x < edge[1], index 1.
            # We want edge[i] <= x < edge[i+1] -> bin i
            # np.searchsorted(edges, x, side='right') returns index where x could be inserted while maintaining order.
            # If x is smaller than all edges, 0. If larger, len(edges).
            # Let's stick to the previous working logic but robustify.
            idx = np.searchsorted(edges, example.context_tokens, side="right") - 1
            idx = min(max(0, idx), q_bins - 1)
            bins[idx].append(example)

        # 4. Merge Sparse Bins (User Requirement: n >= 10 statistical power)
        # Strategy: Iterate from end (longest context) backwards. If a bin is sparse, merge into the one before it.
        # Actually, if bin 9 is sparse, merge with 8. If 8 is sparse, merge with 7.
        # Merged bins will effectively reduce the number of bins but increase density.
        
        # We process from last to second-to-last
        # Using a fresh list for merged bins to avoid index confusion
        merged_bins = []
        
        # We'll just iterate and collect. 
        # A better approach for "Merging":
        # Check counts relative to n_per_bin or hard limit 10? User said "n < 10".
        MIN_SAMPLES = 10 
        
        # We will do a pass: if bin[i] < MIN_SAMPLES, combine it with bin[i-1].
        # Exception: Bin 0. If Bin 0 is sparse, we might have to merge Bin 1 into it? 
        # Actually standard practice is usually merge small tails into larger bodies.
        # User specified: "If 90-100th (last bin) has n=2, merge with 80-90th."
        
        # Working backwards
        final_bins_map = {} # Map old_index -> examples
        
        # First pass: clean up empty lists
        # (Though our quantile method guarantees ~equal counts if distribution is smooth. 
        # Sparsity happens if buffer is small or distribution is discrete.)
        
        current_pool = []
        current_indices = []
        
        # Let's try a forward pass to build valid chunks? 
        # No, user specifically mentioned tail sparsity.
        # Let's stick to the specific instruction: Merge top bin down if sparse.
        
        for i in range(q_bins - 1, 0, -1): # 9 down to 1
            if len(bins[i]) < MIN_SAMPLES and len(bins[i]) > 0:
                print(f"Bin {i} is sparse ({len(bins[i])} items). Merging into Bin {i-1}.")
                bins[i-1].extend(bins[i])
                bins[i] = [] # Clear it
        
        # Now collect samples
        selected_examples = []
        for i in range(q_bins):
            current_bin = bins[i]
            if not current_bin: continue
            
            # Re-calculate range for reporting
            bin_min = min(ex.context_tokens for ex in current_bin)
            bin_max = max(ex.context_tokens for ex in current_bin)
            
            if len(current_bin) <= n_per_bin:
                print(f"Bin {i} (merged range {bin_min}-{bin_max} t): Taking all {len(current_bin)}")
                selected_examples.extend(current_bin)
            else:
                print(f"Bin {i} (merged range {bin_min}-{bin_max} t): Sampling {n_per_bin} of {len(current_bin)}")
                selected_examples.extend(random.sample(current_bin, n_per_bin))

    # 5. Serialize
    manifest_data = [asdict(example) for example in selected_examples]

    with open("manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=4)

    print(f"Saved {len(selected_examples)} samples to manifest.json")
    elapsed_time = time.perf_counter() - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")

    return selected_examples