# 本模块主要用来实现将文本转化为向量，构建向量索引，相似度计算


from .embedding import EmbeddingGenerator
from .index_storage import sqlightvec
__all__ = ['EmbeddingGenerator','sqlightvec']




'''
sqlight-vec
    def create_vector_table(VECTOR_DIM = 768) 创建初始的表，这里的参数是向量的维度
    def insert_vector(content: str, embedding: np.ndarray)
    def search_similar_vectors(query_embedding: np.ndarray, top_k: int = 5) 
        """
            检索与查询向量最相似的结果
            :param query_embedding: 查询向量
            :param top_k: 返回前k个相似结果
            :return: 相似结果列表（包含内容、相似度）
        """
        formatted_results = [
                {
                    "id": res[0],
                    "content": res[1],
                    "cosine_similarity": 1 - res[2]  # 距离转相似度（余弦相似度范围0-1）
                }
                for res in results
            ]
    
'''



'''
EmbeddingGenerator
    def __init__(
        self,
        model_path: str = None,  # 默认从环境变量 EMBEDDING_MODEL_PATH 读取
        n_ctx: int = 512,
        n_threads: int = 4,
        embedding: bool = True
    ):
    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True
    ) -> np.ndarray:
    def similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
'''