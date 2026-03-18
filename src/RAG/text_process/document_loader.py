"""
文档加载模块
支持：Markdown (.md) + PDF (.pdf)
"""

import os
from pathlib import Path
from typing import List, Dict
import pdfplumber

class Document:
    """单个文档"""
    def __init__(self, content: str, source: str, doc_type: str):
        self.content = content      # 文档内容
        self.source = source        # 文件路径
        self.doc_type = doc_type    # md / pdf

class DocumentLoader:
    """批量加载知识库文档"""
    def load_directory(self, path: str) -> List[Document]:
        p = Path(path)
        a =  [str(x) for x in p.iterdir() if x.is_file()]
        return a
    
    def load_pdf(self, file_path: str) -> str:
        """提取PDF文本（按页分段）"""
        with pdfplumber.open(file_path) as pdf:
            full_text = ''
            for page, pagenum in zip(pdf.pages, range(len(pdf.pages))):
                #print(f'第{pagenum + 1}页：')
                #print(page.extract_text())
                full_text += page.extract_text() + '\n'
        return full_text.strip()
    def load_markdown(self, file_path: str):
        """读取Markdown"""
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        return md_content.strip()
        

