print('hello')

from . import text_process
from .text_process import *
from .build_index import *
from .llm_generate import *
from .retrieve import *
import numpy as np


class RAG:
    def __init__(self,vec_db_path):
        self.knowledge_path = None
        self.pdf_docs = None
        self.chunks = None
        self.embeddings = None
        self.vec_db_path = vec_db_path
        self.llm = LLM('')
    def _read_pdf(self):
        ### 1. 读取目录
        documentloader = DocumentLoader()
        print(text_process.__author__)
        print(documentloader.load_directory(self.knowledge_path))
        pdf_doc_route = documentloader.load_directory(self.knowledge_path)

        ### 2. 读取pdf文件
        pdf_docs = [] # 全部pdf的文本文件
        for doc in pdf_doc_route:
            pdf_docs.append(Document(documentloader.load_pdf(doc),doc,'pdf'))
        self.pdf_docs = pdf_docs
    def _chunk_documents(self):
        ### 3. 文档分块
        chunks = []
        textChunker = TextChunker()
        for pdf_doc in self.pdf_docs:
            chunks.extend(textChunker.chunk_by_paragraph(pdf_doc.content,pdf_doc.source)) # 通过段落进行文档分块
        print(chunks[0].text) # 测试是否分块成功
        self.chunks = chunks
    def _embedding(self):
        ### 4. 文档块embedding
        #embeddingGenerator = EmbeddingGenerator(model_path = "/path/to/your/model.gguf") 可以切换到你的模型
        embeddingGenerator = EmbeddingGenerator()
        embeddings = []
        for chunk in self.chunks:
            embeddings.append(embeddingGenerator.encode(chunk.text))
        self.embeddings = embeddings
    
    def compute_similarities(queryA,queryB):
        print(f'计算{queryA}和{queryB}的相关性')
        embeddingGenerator = EmbeddingGenerator()
        queryA_vec = embeddingGenerator.encode(queryA)
        queryB_vec = embeddingGenerator.encode(queryB)

        # 计算余弦相似度
        similaritie = np.dot(queryA_vec, queryB_vec.T).flatten()
        print(similaritie)
    def init_vec_db(self,knowledge_path = '../knowledge_base'):
        self.vec_db_path = self.vec_db_path
        self.knowledge_path = knowledge_path
        ### 1. 读取文件
        self._read_pdf()
        ### 2. 分块
        self._chunk_documents()
        ### 3. embedding
        self._embedding()
        ### 4. 创建向量数据库并将文本和向量存储到里面去
        sqlight = sqlightvec(self.vec_db_path)
        sqlight.create_vector_table(VECTOR_DIM = 768)
        chunk_vec = [(chunk.text,vec) for chunk,vec in zip(self.chunks,self.embeddings)]
        for content,embedding in chunk_vec:
            sqlight.insert_vector(content, embedding)

    def retrieve_for_query(self,query:str,top_k = 5):
        retrieve = Retriever(self.vec_db_path)

        return retrieve.retrieve_mix(query,top_k)


    def generate_answer(self,query):
        return self.llm.chat(query)

    def retrieval_augmented_generate(self,query):
        results = self.retrieve_for_query(query)
        print(len(results))
        result = ''
        for i in results:
            result+=i['content']
        question = result+'\n请根据上述信息回答下面问题\n'+query

        print(result)
        return self.generate_answer(question)

def get_abs_path(relative_path):
    """
    获取相对于当前代码文件的绝对路径
    :param relative_path: 相对于当前文件的路径
    :return: 绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

import os
def main():
    print('hello')

    rag = RAG('../sqlight/vec_3.db')
    # 初始化向量数据库（如果没创建的话）
    rag.init_vec_db(knowledge_path = get_abs_path('../../knowledge_base'))
    # 查询
    # result = rag.retrieve_for_query('第二课堂包含哪些课程类别？')
    # print(rag.generate_answer(result))


if __name__ == "__main__":
    print(get_abs_path('../../knowledge_base'))
    main()