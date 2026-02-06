
import os
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from .client import ModelClient

load_dotenv()

class OpenAIClient(ModelClient):
    """Client for OpenAI API models."""
    
    # Pricing cache (approximate, per 1M tokens) - Update as needed
    PRICING = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous generation with simple retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0, # Deterministic
                    **kwargs
                )
                
                # Capture usage
                if response.usage:
                    self.last_usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                
                return response.choices[0].message.content or ""
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt) # Exponential backoff
        return ""

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage

    def cost_estimate(self, prompt_tokens: int, max_completion_tokens: int) -> float:
        if self.model_name not in self.PRICING:
            return 0.0 # Unknown model
            
        rate = self.PRICING[self.model_name]
        input_cost = (prompt_tokens / 1_000_000) * rate["input"]
        output_cost = (max_completion_tokens / 1_000_000) * rate["output"]
        return input_cost + output_cost
