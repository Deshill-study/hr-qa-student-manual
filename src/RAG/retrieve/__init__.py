from .retriever import Retriever

__all__ = ['Retriever']

'''
def __init__(self,vec_db_path):
def base_vec_distance_cosine(self,query,top_k = 5): ->list[dict{id:int,content:str,cosine_similarity:float}]
def retrieve_mix(self, query: str, top_k: int = 7, use_rerank: bool = True) -> List[Dict]:  {id:int,  content:str,  cosine_similarity:float,  rrf_score:float,  vector_rank: int,   keyword_rank: int, 'relevance_score': 3.0}
'''
'''
        for item in sorted_docs[:top_k]:
            doc = item['doc'].copy()
            doc['rrf_score'] = item['rrf_score']
            doc['vector_rank'] = item['vector_rank']
            doc['keyword_rank'] = item['keyword_rank']
            results.append(doc)
'''



