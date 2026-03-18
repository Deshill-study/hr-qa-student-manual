## 此module用来处理文本，包括文本的读取，文本分块
from .document_loader import Document,DocumentLoader
from.text_chunker import DocumentChunk,TextChunker

__all__ = ['Document','DocumentLoader','TextChunker','DocumentChunk']
__author__ = 'Deshill'

'''
Document:
    def __init__(self, content: str, source: str, doc_type: str):
        self.content = content      # 文档内容
        self.source = source        # 文件路径
        self.doc_type = doc_type    # md / pdf


DocumentLoader:
    def load_directory(self, path: str) -> List[Document]:
    def load_pdf(self, file_path: str) -> str:
'''

'''
DocumentChunk:
    def __init__(self, text: str, source: str, chunk_id: str, embedding: np.ndarray = None):
        self.text = text              # 文本内容
        self.source = source          # 来源文件
        self.chunk_id = chunk_id      # 唯一ID
        self.embedding = embedding    # 向量表示

TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
            """
            Args:
                chunk_size: 每个块的最大字符数
                overlap: 相邻块之间的重叠字符数（保持上下文连贯）
            """
            self.chunk_size = chunk_size
            self.overlap = overlap
    def chunk_by_paragraph(self, text: str, source: str) -> List[DocumentChunk]:
'''