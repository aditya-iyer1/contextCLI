# Implements natural length distribution (NLDA) and verification detection (Wang, et al. 2026).
# Tokenizes a large buffer and pulls N samples per quantile

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

1. Load reference token
2. Length scanning: a function to scan a buffer (e.g. 1000-2000 samples) and calculate the natural token counts
3. quantile calculation: Logic to determine the boundaries for 10 bins lie based on the buffer's distribution
4. Stratified Selection: Logic to sleect N samples form each bin
'''

from datasets import load_dataset
import tiktoken
import os, json, random, time
from dotenv import load_dotenv
from contextcliff.data import formats
import numpy as np
from dataclasses import asdict

load_dotenv()
HF_TOKEN = os.getenv("HF_Token")

SYSTEM_PROMPT = (
    "You are reading a comprehension system."
    "Answer the question based only on the provided context.\n\n"
)


if HF_TOKEN is None:
    raise ValueError("API_TOKEN not found in environment variables or .env file")


def build_context(item):
        return (
            SYSTEM_PROMPT
            + "Context:\n"
            + item["document"]["text"]
            + "\n\nQuestion:\n"
            + item["question"]["text"]
        )

def balance_samples(n_per_bin: int = 10, buffer_size: int = 2000):
    """
    Loads and balances the samples in the NarrativeQA dataset to ensure each bin has approximately the same number of samples.
    """
    start_time = time.perf_counter()

    # 1. Load & Stream dataset, stream to avoid disk usage
    dataset = load_dataset("narrativeqa", streaming=True, split="test", token=HF_TOKEN)
    print("Done loading dataset!")
    enc = tiktoken.get_encoding("o200k_base") # GPT-4o standard tokenizer

    # 2. Stream & Tokenize
    print(f"Streaming and tokenizing {buffer_size} samples...")
    examples = []

    for i, item in enumerate(dataset):
        if i >= buffer_size: break

        # Built and encode prompt with context
        context = build_context(item)
        t_len = len(enc.encode(context))

        # Clean answers to strings
        ans_strings = [a["text"] for a in item["answers"]] if isinstance(item["answers"][0], dict) else item["answers"]
        
        # Map to formats.Example object
        examples.append(formats.Example(
            id=item["document"]["id"],
            context=context,
            question=item["question"]["text"],
            answers=ans_strings,
            context_tokens=t_len,
            metadata= {"summary": item["document"]["summary"]}
        ))

        
    # 4. Calculate lengths and create example objects
    # print(buffer[0].keys())
    # print(buffer[0]["document"].keys())
    # print(buffer[0]["question"].keys())
    # print(type(buffer[0]["answers"]), len(buffer[0]["answers"]))


    # examples = []
    # for item in buffer:
        
    #     context = build_context(item)   # Build the context string

    #     tokens = enc.encode(context)   # Tokenize the context string
    #     total_context_len = len(tokens)   # Get the total number of tokens in the context string

    #     doc_len = len(enc.encode(item["document"]["text"]))
    #    total_len = len(enc.encode(context))   # Get the total number of tokens in the context string
        
        # context = item["document"]["text"] + " " + item["question"]["text"]
        # token_count = len(enc.encode(context))
            
    #    example = formats.Example(
     #       id=item["document"]["id"],
      #      context=context,
      #      question=item["question"]["text"],
      #      answers=item["answers"],                    # List of strings, need to check against all acceptable answers and take max score amongst them
      #      context_tokens=total_len,
      #      metadata= {"summary": item["document"]["summary"]}
      #  )
      #  examples.append(example)

    # del buffer           # Free up memory by deleting the buffer

    # 5. Sort and Bin logic (as we discussed previously)

    # 5.1: Order samples to identify "long tail"
    examples.sort(key=lambda x: x.context_tokens)
    lengths = [example.context_tokens for example in examples]
    
    # 5.2: Calculate quantiles edges of buffer
    edges = np.quantile(lengths, np.linspace(0, 1, 11))

    # 5.3: Stratified Selection
    # Select N samples from each bin from buffer to create final manifest
    selected_examples = []
    bins = [[] for _ in range(10)]

    # 5.3.1: Segment sorted list into 10 sub-lists based on the boundaries found in the previous step
    for example in examples:
        idx = np.searchsorted(edges, example.context_tokens, side="right") - 1
        idx = min(max(0, idx), 9)
        bins[idx].append(example)

    # 5.3.2: From each sub-list, pick n_per_bin samples
    for i, current_bin in enumerate(bins):
        lower, upper = edges[i], edges[i+1]

        if not current_bin:
            print(f"Bin {i} ({int(lower)}-{int(upper)}): Empty. Skipping.")
            continue

        # If it's the very last bin, include the upper bound
        # if i == 9:
        #    current_bin = [ex for ex in examples if lower <= ex.context_tokens <= upper]
        #else:
        #     current_bin = [ex for ex in examples if lower <= ex.context_tokens < upper]
        
        

        # 5.3.3: Sample from current bin
        if len(current_bin) <= n_per_bin:
            # Take everything if we are under the budget for this bin
            print(f"Bin {i} ({int(lower)}-{int(upper)} tokens): Taking all {len(current_bin)} samples.")
            selected_examples.extend(current_bin)
        else:
            # Downsample to keep the manifest lean and cost-aware
            print(f"Bin {i} ({int(lower)}-{int(upper)} tokens): Sampling {n_per_bin} from {len(current_bin)}.")
            selected_examples.extend(random.sample(current_bin, n_per_bin))

  
    # 5. Creates manifest so the runner can execute without re-streaming, can use pydantic for more robust serialization

    manifest_data = [asdict(example) for example in selected_examples]

    with open("manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=4)

    print(f"Saved {len(selected_examples)} samples to manifest.json")

    elapsed_time = time.perf_counter() - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")

    return selected_examples