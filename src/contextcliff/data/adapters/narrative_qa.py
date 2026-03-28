import os
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import tiktoken
from datasets import load_dataset
from dotenv import find_dotenv, load_dotenv

from contextcliff.data.adapters.base import BaseAdapter
from contextcliff.data.formats import Example


def _load_dotenv_for_hf() -> None:
    """Load `.env` from cwd (if present), then from the nearest directory containing `pyproject.toml` when run from a checkout."""
    load_dotenv(find_dotenv(filename=".env", usecwd=True))
    here = Path(__file__).resolve()
    for d in [here.parent, *here.parents]:
        if (d / "pyproject.toml").is_file():
            load_dotenv(d / ".env")
            break


_load_dotenv_for_hf()


def _resolve_hf_token() -> Optional[str]:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN") or None


class NarrativeQAAdapter(BaseAdapter):
    """Adapter for NarrativeQA dataset from HuggingFace."""
    
    SYSTEM_PROMPT = (
        "You are reading a comprehension system."
        "Answer the question based only on the provided context.\n\n"
    )

    def __init__(self, tokenizer_name: str = "o200k_base"):
        self.hf_token = _resolve_hf_token()
        # We allow tokenizer to be configurable
        try:
            self.enc = tiktoken.get_encoding(tokenizer_name)
        except:
             # Fallback or specific handling for other models could go here
             # For now, default to cl100k_base or similar if specific not found, 
             # but "o200k_base" is standard for GPT-4o
             self.enc = tiktoken.get_encoding("cl100k_base")

    def _build_context(self, item: Dict[str, Any]) -> str:
        return (
            self.SYSTEM_PROMPT
            + "Context:\n"
            + item["document"]["text"]
            + "\n\nQuestion:\n"
            + item["question"]["text"]
        )

    def load_stream(self) -> Iterator[Example]:
        """Streams examples from HF."""
        # Using streaming=True to handle large datasets
        dataset = load_dataset(
            "narrativeqa",
            streaming=True,
            split="test",
            token=self.hf_token,
        )
        
        for item in dataset:
            context = self._build_context(item)
            # Tokenize using the selected tokenizer
            # Note: For non-OpenAI models, we might need a HuggingFace tokenizer here.
            # Keeping tiktoken for now as per previous, but structure allows swapping self.enc
            t_len = len(self.enc.encode(context))
            
            # Clean answers
            raw_answers = item["answers"]
            ans_strings = [a["text"] for a in raw_answers] if (raw_answers and isinstance(raw_answers[0], dict)) else raw_answers

            yield Example(
                id=f"{item['document']['id']}_{hash(item['question']['text'])}",
                context=context,
                question=item["question"]["text"],
                answers=ans_strings,
                context_tokens=t_len,
                metadata={"summary": item["document"]["summary"]}
            )
