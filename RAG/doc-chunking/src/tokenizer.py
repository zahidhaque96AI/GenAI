
from typing import Protocol
import tiktoken

class Tokenizer(Protocol):
    
    def count_tokens(self, text: str) -> int:
        ...
        
class TiktokenTokenizer:
    
    def __init__(self, encoding_name: str = "cl100k_base") -> None:
        try:
            self._encoding = tiktoken.get_encoding(encoding_name)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported tokenizer encoding: {encoding_name}"
            )  from exec
            
    def encode(self, text: str) -> list[int]:
        return self._encoding.encode(
            text, allowed_special=set()
        )
        
    def decode(self, tokens: list[int]) -> str:
        return self._encoding.decode(tokens)
    
    def count_tokens(self, text: str) -> int:
        return len(self.encode(text))