# Implements natural length distribution (NLDA) and verification detection (Wang, et al. 2026).
# Tokenizes a large bugger and pulls N samples per quantile

'''
Internal logic:
1. Ingest: Load NarrativeQA via HuggingFace Datasets
2. Tokenize: Use tiktoken to get the natural length
3. Sort: Rank the entire buffer by token count
4. Quantize: Use numpy.quantile or similar to find the boundaries for 10 jobs
5. Sample: Select N items from each bin and save them to a manifest.json

- If NarrativeQA turns out to have no samples between 80k and 128k tokens, will find out now (for free) rather than after building broken runner
- manifest.json acts as a "budget contract", to tell exactly how many tokens we are about to process before hitting run

- Install tiktoken and datasets (huggingface) in environment
- tokenizer: Am i ok using o200k_base (gpt4o) as reference tokenizer? Good industry proxy.
'''