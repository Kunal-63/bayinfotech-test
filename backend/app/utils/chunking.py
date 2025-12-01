"""Document chunking strategies for RAG pipeline."""
from typing import List, Dict, Any
import re


class TextChunker:
    """Text chunking strategies with optional overlap."""
    
    @staticmethod
    def sliding_window_chunks(
        text: str,
        chunk_size: int = 512,
        overlap: int = 100,
        delimiter: str = " "
    ) -> List[str]:
        """
        Split text into overlapping chunks using sliding window.
        
        Args:
            text: Text to chunk
            chunk_size: Target size per chunk (in "tokens"/words)
            overlap: Number of overlapping tokens between consecutive chunks
            delimiter: Delimiter to split on (typically space for word-based)
        
        Returns:
            List of chunk strings
        """
        if not text or not text.strip():
            return []
        
        # Split into tokens (words)
        tokens = text.split(delimiter)
        
        if len(tokens) <= chunk_size:
            return [text]
        
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i : i + chunk_size]
            chunk_text = delimiter.join(chunk_tokens)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            # Stop if we've reached the end
            if i + chunk_size >= len(tokens):
                break
        
        return chunks
    
    @staticmethod
    def semantic_chunks(
        text: str,
        chunk_size: int = 512,
        overlap: int = 100,
        delimiters: List[str] = None
    ) -> List[str]:
        """
        Split text at sentence/paragraph boundaries, respecting max chunk size.
        
        Useful for preserving logical boundaries (e.g., paragraphs, sentences).
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in words
            overlap: Overlap in words between chunks
            delimiters: Boundary delimiters (e.g., ["\n\n", "\n", ". ", " "])
        
        Returns:
            List of chunk strings
        """
        if not text or not text.strip():
            return []
        
        if delimiters is None:
            delimiters = ["\n\n", "\n", ". ", " "]
        
        # Split at first available delimiter
        current_delimiter = delimiters[0] if delimiters else " "
        for delim in delimiters:
            if delim in text:
                current_delimiter = delim
                break
        
        segments = text.split(current_delimiter)
        chunks = []
        current_chunk = []
        current_chunk_tokens = 0
        
        for segment in segments:
            segment_tokens = len(segment.split())
            
            # If adding this segment would exceed chunk_size, save current chunk and start new one
            if current_chunk and (current_chunk_tokens + segment_tokens) > chunk_size:
                chunk_text = current_delimiter.join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)
                
                # Start new chunk with overlap from last segments
                overlap_segments = int(overlap / max(len(" ".join(current_chunk).split()), 1))
                current_chunk = current_chunk[-overlap_segments:] if overlap_segments > 0 else []
                current_chunk_tokens = sum(len(s.split()) for s in current_chunk)
            
            current_chunk.append(segment)
            current_chunk_tokens += segment_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = current_delimiter.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks
    
    @staticmethod
    def sentence_chunks(
        text: str,
        chunk_size: int = 512,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into sentence-based chunks with sliding window overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in words
            overlap: Overlap in words between chunks
        
        Returns:
            List of chunk strings
        """
        if not text or not text.strip():
            return []
        
        # Simple sentence splitting: split on ., !, ?
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_words = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed chunk_size, save and start new
            if current_chunk and (current_words + sentence_words) > chunk_size:
                chunk_text = " ".join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)
                
                # Overlap: keep last N words
                last_sentence_words = len(current_chunk[-1].split()) if current_chunk else 0
                if overlap > 0 and last_sentence_words < overlap:
                    # Keep last sentence if it fits in overlap
                    current_chunk = current_chunk[-1:] if current_chunk else []
                    current_words = last_sentence_words
                else:
                    current_chunk = []
                    current_words = 0
            
            current_chunk.append(sentence)
            current_words += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks


class DocumentChunker:
    """Document-aware chunker that preserves metadata."""
    
    @staticmethod
    def chunk_document(
        title: str,
        content: str,
        doc_metadata: Dict[str, Any],
        chunk_size: int = 512,
        overlap: int = 100,
        strategy: str = "sliding_window"
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document and return chunks with metadata.
        
        Args:
            title: Document title
            content: Document content
            doc_metadata: Document metadata (will be copied to each chunk)
            chunk_size: Target chunk size in tokens/words
            overlap: Overlap between chunks in tokens/words
            strategy: Chunking strategy ("sliding_window", "semantic", "sentence")
        
        Returns:
            List of chunk dicts with keys: content, chunk_index, chunk_count, 
            original_doc_title, doc_metadata
        """
        if strategy == "sliding_window":
            chunk_texts = TextChunker.sliding_window_chunks(
                content, chunk_size=chunk_size, overlap=overlap
            )
        elif strategy == "semantic":
            chunk_texts = TextChunker.semantic_chunks(
                content, chunk_size=chunk_size, overlap=overlap
            )
        elif strategy == "sentence":
            chunk_texts = TextChunker.sentence_chunks(
                content, chunk_size=chunk_size, overlap=overlap
            )
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
        
        # If no chunks (empty content), return at least one empty chunk
        if not chunk_texts:
            chunk_texts = [content] if content else [""]
        
        chunks = []
        for i, chunk_text in enumerate(chunk_texts):
            chunk_metadata = doc_metadata.copy() if doc_metadata else {}
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_count"] = len(chunk_texts)
            chunk_metadata["original_doc_title"] = title
            
            chunks.append({
                "content": chunk_text,
                "chunk_index": i,
                "chunk_count": len(chunk_texts),
                "original_doc_title": title,
                "doc_metadata": chunk_metadata
            })
        
        return chunks
