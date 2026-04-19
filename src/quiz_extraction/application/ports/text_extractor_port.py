from abc import ABC, abstractmethod

class TextExtractorPort(ABC): 
    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str)  -> str:
        ...