import sqlite3
import numpy as np
from typing import List, Tuple, Dict
import json
import hashlib
class DocumentChunk:
    """文档片段"""
    def __init__(self, text: str, source: str, chunk_id: str, embedding: np.ndarray = None):
        self.text = text              # 文本内容
        self.source = source          # 来源文件
        self.chunk_id = chunk_id      # 唯一ID
        self.embedding = embedding    # 向量表示
    
    def __repr__(self):
        return f"Chunk(id={self.chunk_id}, text_len={len(self.text)}, source={self.source})"


class TextChunker:
    """
    文档分块器
    将长文本切分成适合检索的小片段
    """
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 150):
        """
        Args:
            chunk_size: 每个块的最大字符数
            overlap: 相邻块之间的重叠字符数（保持上下文连贯）
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_paragraph(self, text: str, source: str) -> List[DocumentChunk]:
        """
        按段落分块
        优先保证段落完整性，如果段落太长再切分
        """
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            if len(para) <= self.chunk_size:
                # 段落较短，直接作为一个块
                chunk_id = hashlib.md5(f"{source}:{i}:{para[:50]}".encode()).hexdigest()[:12]
                chunks.append(DocumentChunk(para, source, chunk_id))
            else:
                # 段落太长，需要进一步切分
                sub_chunks = self._split_long_text(para, source, i)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_long_text(self, text: str, source: str, para_idx: int) -> List[DocumentChunk]:
        """将长文本按固定大小切分，带重叠"""
        chunks = []
        start = 0
        chunk_idx = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # 尽量在句子边界切分
            if end < len(text):
                # 找最近的句号、问号、换行
                for sep in ['。', '？', '!', '\n', ' ']:
                    pos = text.rfind(sep, start, end)
                    if pos > start + self.chunk_size // 2:  # 至少保留一半内容
                        end = pos + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = hashlib.md5(f"{source}:{para_idx}:{chunk_idx}:{chunk_text[:30]}".encode()).hexdigest()[:12]
                chunks.append(DocumentChunk(chunk_text, source, chunk_id))
            
            # 下一个块的起始位置（带重叠）
            start = end - self.overlap if end < len(text) else end
            chunk_idx += 1
        
        return chunks