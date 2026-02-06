
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ModelClient(ABC):
    """Abstract base class for all model backends (API or Local)."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The full prompt string.
            **kwargs: Additional model-specific parameters (e.g., max_tokens).
            
        Returns:
            The generated text string.
        """
        pass

    @abstractmethod
    def get_token_usage(self) -> Dict[str, int]:
        """Return token usage stats for the last call (prompt, completion, total)."""
        pass
        
    @abstractmethod
    def cost_estimate(self, prompt_tokens: int, max_completion_tokens: int) -> float:
        """Estimate cost for a request."""
        pass
