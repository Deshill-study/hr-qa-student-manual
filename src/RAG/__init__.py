from .rag import RAG
__all__ = ['RAG']

'''
RAG类使用方法
RAG('vec_db_path') 引入存放索引数据库的地址
init_vec_db(self,knowledge_path = '../knowledge_base') 引入文档库的地址，数据库如果是刚刚创建的话或者文档库有所更新就要加上这个

retrieve_for_query(self,query:str,top_k = 5)  -> List[Dict]:  {id:int,  content:str,  cosine_similarity:float,  rrf_score:float,  vector_rank: int,   keyword_rank: int, 'relevance_score': 3.0}
使用混合排序，向量排序+关键词排序，然后再用RRF计算综合排序，然后再让llm进行重排序，返回出来top_k的相关文档

generate_answer(query) -> 调用大语言模型回答query的问题

retrieval_augmented_generate(self,query) -> str 直接一条龙服务，检索增强生成

compute_similarities(queryA,queryB) -> float((0,1))计算语句A和语句B的相关性

'''

'''
使用样例
print('hello')
rag = RAG('../sqlight/vec_2.db')
# 初始化向量数据库（如果没创建的话）
rag.init_vec_db(knowledge_path = '../knowledge_base')
print(rag.retrieval_augmented_generate('计算机与信息安全学院志愿服务综合测评加分有几种方式？'))
'''

