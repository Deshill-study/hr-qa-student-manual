import sqlite3
import sqlite_vec
import numpy as np
import os
import re
import jieba
from typing import List, Dict
import numpy as np
from ..build_index import EmbeddingGenerator
from ..build_index import sqlightvec
from ..llm_generate import LLM
# from src.RAG.build_index import EmbeddingGenerator
# from src.RAG.build_index import sqlightvec
# from src.RAG.llm_generate import LLM

class Retriever:
    def __init__(self,vec_db_path):
        self.top_k = 10
        self.vec_db_path = vec_db_path
        self.stopwords = {
            '的', '了', '是', '在', '就', '都', '而', '及', '与', '或',
            '包含', '哪些', '什么', '如何', '怎么', '为什么', '请', '问'
        }
        # 从环境变量读取 API Key
        self.llm = LLM()
        self.embeddingGenerator = EmbeddingGenerator()
        self.sqlight = sqlightvec(self.vec_db_path)
    def search_base_vector(self,query,top_k = 5):#向量检索
        query_vec = self.embeddingGenerator.encode(query)
        results = self.sqlight.search_similar_vectors(query_embedding = query_vec,top_k = top_k)

        return results
        # ### 9. 展示结果
        # res = ''
        # for result in results:
        #     #print(result['content'])
        #     res+=result['content']
        # return res
    def search_base_keyword(self, query: str, top_k: int = 10) -> List[Dict]:
        all_docs = self._get_all_documents()
        
        query_words = set(jieba.lcut(query))
        query_words = query_words - self.stopwords
        
        if len(query_words) == 0:
            return []
        
        scored = []
        for doc in all_docs:
            doc_words = set(jieba.lcut(doc['content']))
            doc_words = doc_words - self.stopwords
            
            union_size = len(query_words | doc_words)
            jaccard = len(query_words & doc_words) / union_size if union_size > 0 else 0
            
            term_bonus = 0
            for word in query_words:
                if word in doc['content']:
                    term_bonus += 0.1
            
            final_score = jaccard + term_bonus
            
            if final_score > 0:
                scored.append({
                    'id': doc.get('id', hash(doc['content'])),
                    'content': doc['content'],
                    'keyword_score': final_score,
                    'source': 'keyword',
                    'matched_words': list(query_words & doc_words)
                })
        
        scored.sort(key=lambda x: x['keyword_score'], reverse=True)
        return scored[:top_k]

    def _get_all_documents(self) -> List[Dict]:
        sqlight = sqlightvec(self.vec_db_path)
        cursor = sqlight.conn.cursor()
        cursor.execute("SELECT id, content FROM document_vectors")
        results = cursor.fetchall()
        return [{'id': res[0], 'content': res[1]} for res in results]
    def retrieve_mix(self, query: str, top_k: int = 7, use_rerank: bool = True) -> List[Dict]:
        """混合检索主方法"""
        # 1. 向量检索（召回 20 个候选）
        vector_results = self.search_base_vector(query, top_k=20)
        # list[dict{id:int,content:str,cosine_similarity:float}]

        # 2. 关键词检索（召回 20 个候选）
        keyword_results = self.search_base_keyword(query, top_k=20)
        '''
        scored.append({
                    'id': doc.get('id', hash(doc['content'])),
                    'content': doc['content'],
                    'keyword_score': final_score,
                    'source': 'keyword',
                    'matched_words': list(query_words & doc_words)
                })
        '''

        # 3. RRF 融合
        fused_results = self._reciprocal_rank_fusion(
            vector_results, keyword_results, top_k=15
        )
        '''
        for item in sorted_docs[:top_k]:
            doc = item['doc'].copy()
            doc['rrf_score'] = item['rrf_score']
            doc['vector_rank'] = item['vector_rank']
            doc['keyword_rank'] = item['keyword_rank']
            results.append(doc)
        '''
        # 4. LLM 重排序
        if use_rerank and len(fused_results) > 0:
            reranked_results = self._rerank_with_llm(query, fused_results, top_k=top_k)
            
            return reranked_results
        else:
            return fused_results[:top_k]

    # ========================= RRF 融合 ===========================
    def _reciprocal_rank_fusion(self, vector_results: List[Dict], 
                                 keyword_results: List[Dict], 
                                 top_k: int = 15) -> List[Dict]:
        rank_map = {}
        
        for i, doc in enumerate(vector_results):
            doc_id = doc.get('id', hash(doc['content']))
            if doc_id not in rank_map:
                rank_map[doc_id] = {
                    'doc': doc.copy(),
                    'vector_rank': i + 1,
                    'keyword_rank': None
                }
            else:
                rank_map[doc_id]['vector_rank'] = i + 1
        
        for i, doc in enumerate(keyword_results):
            doc_id = doc.get('id', hash(doc['content']))
            if doc_id not in rank_map:
                rank_map[doc_id] = {
                    'doc': doc.copy(),
                    'vector_rank': None,
                    'keyword_rank': i + 1
                }
            else:
                rank_map[doc_id]['keyword_rank'] = i + 1
        
        k = 60
        for doc_id, info in rank_map.items():
            rrf_score = 0
            if info['vector_rank']:
                rrf_score += 1 / (k + info['vector_rank'])
            if info['keyword_rank']:
                rrf_score += 1 / (k + info['keyword_rank'])
            info['rrf_score'] = rrf_score
        
        sorted_docs = sorted(rank_map.values(), key=lambda x: x['rrf_score'], reverse=True)
        
        results = []
        for item in sorted_docs[:top_k]:
            doc = item['doc'].copy()
            doc['rrf_score'] = item['rrf_score']
            doc['vector_rank'] = item['vector_rank']
            doc['keyword_rank'] = item['keyword_rank']
            results.append(doc)
        
        return results
    def _rerank_with_llm(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        scored = []
        
        for i, candidate in enumerate(candidates):
            content = candidate['content'][:800]
            
            prompt = f"""请判断以下文档与查询的相关性，打分 0-10 分：

查询：{query}

文档：{content}

评分标准：
- 0-2 分：完全无关
- 3-5 分：部分相关
- 6-8 分：大部分相关
- 9-10 分：完全相关

只返回一个数字（0-10）："""
            
            try:
                response = self.llm.chat(prompt)
                match = re.search(r'\d+', response)
                score = float(match.group()) if match else 5.0
                score = min(10, max(0, score))
            except Exception as e:
                print(f"重排序出错：{e}")
                score = 5.0
            
            scored.append((candidate, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scored[:top_k]:
            doc_copy = doc.copy()
            doc_copy['relevance_score'] = score
            results.append(doc_copy)
        
        return results
    
if __name__=="__main__":
    a = 1
    retrieve = Retriever(vec_db_path = '/root/.openclaw/workspace/hr-assistant/sqlight/vec_3.db')
    