#### 将文本转为向量，计算向量相似度

from typing import List, Union
from llama_cpp import Llama
import numpy as np
import os


class EmbeddingGenerator:
    """
    基于 llama.cpp 的本地 Embedding 生成器
    使用 GGUF 格式模型
    
    ⚠️ 配置说明：
    - 模型路径可通过环境变量配置：EMBEDDING_MODEL_PATH
    - 或修改 DEFAULT_MODEL_PATH 常量
    - 推荐下载 Q8_0 量化版本（约 300MB）
    """
    
    # 默认模型路径（可修改）
    DEFAULT_MODEL_PATH = os.getenv(
        'EMBEDDING_MODEL_PATH',
        os.path.expanduser("~/.node-llama-cpp/models/nomic-embed-text-v1.5.Q8_0.gguf")
    )
    
    def __init__(
        self,
        model_path: str = None,
        n_ctx: int = 512,
        n_threads: int = 4
    ):
        """
        初始化 Embedding 生成器
        
        Args:
            model_path: GGUF 模型路径（默认从环境变量或默认路径读取）
            n_ctx: 上下文长度
            n_threads: 使用的线程数
        """
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.embedding_dim = 768
        
        # 检查模型文件是否存在
        if not os.path.exists(self.model_path):
            print(f"⚠️ 警告：Embedding 模型文件不存在：{self.model_path}")
            print("请从以下地址下载：")
            print("  - HuggingFace: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF")
            print("  - ModelScope: https://modelscope.cn/models/nomic-ai/nomic-embed-text-v1.5-GGUF")
            print(f"下载后放置到：{self.model_path}")
        
        # 加载模型
        print(f"正在加载 Embedding 模型：{self.model_path}")
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            embedding=True,
            verbose=False,
            n_gpu_layers=0  # 纯 CPU 运行，如需 GPU 加速可调整
        )
        print(f"✅ 模型加载完成，向量维度：{self.embedding_dim}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True
    ) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            normalize: 是否归一化向量（L2 范数）
        
        Returns:
            向量数组 (N, 768)
        """
        # 统一转为列表
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        
        for text in texts:
            # 截断超长文本
            if len(text) > self.n_ctx * 4:
                text = text[:self.n_ctx * 4]
            
            # 生成 embedding
            output = self.llm.embed(text)
            embeddings.append(output)
        
        # 转为 numpy 数组
        embeddings = np.array(embeddings)
        
        # L2 归一化
        if normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        计算两个文本的相似度（余弦相似度）
        
        Returns:
            相似度分数 (0 ~ 1)
        """
        emb1, emb2 = self.encode([text1, text2], normalize=True)
        return float(np.dot(emb1, emb2))
    
    def batch_encode(
        self,
        texts: List[str],
        batch_size: int = 8
    ) -> np.ndarray:
        """
        批量编码（带进度显示）
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
        
        Returns:
            向量数组 (N, 768)
        """
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.encode(batch, normalize=True)
            all_embeddings.append(batch_embeddings)
            
            if (i // batch_size + 1) % 10 == 0:
                print(f"已处理：{min(i + batch_size, len(texts))}/{len(texts)}")
        
        return np.vstack(all_embeddings)
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'llm'):
            del self.llm


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 初始化生成器
    embedder = EmbeddingGenerator()

    # 单文本编码
    text = "OpenClaw 是一个 AI 智能体框架"
    vector = embedder.encode(text)
    print(f"\n文本：{text}")
    print(f"向量维度：{vector.shape}")
    print(f"向量前 5 个值：{vector[0, :5]}")

    # 批量编码
    texts = [
        "OpenClaw 智能体框架",
        "QQ 机器人开发",
        "桂林电子科技大学",
        "金丝熊仓鼠喜欢吃香蕉干"
    ]
    vectors = embedder.encode(texts)
    print(f"\n批量编码：{vectors.shape}")

    # 计算文本相似度
    sim = embedder.similarity(
        "OpenClaw 是 AI 框架",
        "OpenClaw 用于开发智能体"
    )
    print(f"\n相似度：{sim:.4f}")

    # 批量相似度搜索
    query = "AI 智能体开发"
    documents = [
        "OpenClaw 是一个 AI 智能体框架",
        "桂林米粉是桂林的特色美食",
        "Python 是一种编程语言",
        "AI 智能体可以自动执行任务"
    ]

    query_vec = embedder.encode(query)
    doc_vecs = embedder.encode(documents)

    # 计算余弦相似度
    similarities = np.dot(doc_vecs, query_vec.T).flatten()

    print(f"\n查询：{query}")
    print("最相关文档:")
    for idx in np.argsort(similarities)[::-1][:3]:
        print(f"  [{similarities[idx]:.4f}] {documents[idx]}")
