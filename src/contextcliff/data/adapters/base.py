
from abc import ABC, abstractmethod
from typing import Iterator
from contextcliff.data.formats import Example

class BaseAdapter(ABC):
    """Abstract base class for dataset adapters."""
    
    @abstractmethod # Enforce implementation by subclasses
    def load_stream(self) -> Iterator[Example]:
        """
        Yields Example objects one by one.
        Must handle its own tokenization logic or standardized content.
        """
        pass
