### 向量数据库存储

import sqlite3
import sqlite_vec
import numpy as np


class sqlightvec:
    def __init__(self, db_path):
        """初始化SQLite-Vec连接"""
        # -------------------------- 1. 初始化数据库连接（解决权限问题） --------------------------
        # 创建连接并启用扩展加载权限
        self.conn = sqlite3.connect(db_path)
        # 关键：启用扩展加载权限（解决 not authorized 错误）
        self.conn.enable_load_extension(True)
        # 启用sqlite-vec扩展
        sqlite_vec.load(self.conn)
        # 关闭扩展加载权限（安全最佳实践）
        self.conn.enable_load_extension(False)
        # 创建游标（作为实例变量，供其他方法使用）
        self.cursor = self.conn.cursor()

    # -------------------------- 2. 创建带向量字段的表 --------------------------
    def create_vector_table(self, VECTOR_DIM=768):
        """创建包含向量字段的虚拟表"""
        # 向量维度根据你的embedding结果调整（示例用768维，可改为你的实际维度）
        
        # 执行建表语句 - 使用 VIRTUAL TABLE 和 float[维度] 语法
        self.cursor.execute(f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS document_vectors USING vec0(
            embedding float[{VECTOR_DIM}],  -- 向量字段（float类型，指定维度）
            content TEXT,                    -- 原始文本内容
            id INTEGER PRIMARY KEY           -- 主键ID
        )
        """)
        self.conn.commit()
        print("向量表创建成功（或已存在）")

    # -------------------------- 3. 插入向量数据 --------------------------
    def insert_vector(self, content: str, embedding: np.ndarray):
        """
        插入向量数据到表中
        :param content: 文本内容
        :param embedding: 向量数组（numpy数组或列表）
        """
        # 确保向量是float32类型并展平
        embedding = np.array(embedding, dtype=np.float32).flatten()
        
        # 插入数据 - 使用 serialize_float32 序列化向量
        self.cursor.execute("""
        INSERT INTO document_vectors (content, embedding)
        VALUES (?, ?)
        """, (content, sqlite_vec.serialize_float32(embedding)))  # 使用 sqlite_vec 序列化
        
        self.conn.commit()
        print(f"成功插入向量：{content[:20]}...")

    # -------------------------- 4. 向量相似度检索 --------------------------
    def search_similar_vectors(self, query_embedding: np.ndarray, top_k: int = 5):
        """
        检索与查询向量最相似的结果
        :param query_embedding: 查询向量
        :param top_k: 返回前k个相似结果
        :return: 相似结果列表（包含内容、相似度）
        """
        
        # 预处理查询向量
        query_embedding = np.array(query_embedding, dtype=np.float32).flatten()
        
        # 执行相似度检索 - 使用正确的函数名 vec_distance_cosine
        self.cursor.execute(f"""
        SELECT 
            id, 
            content, 
            vec_distance_cosine(embedding, ?) as distance
        FROM document_vectors
        ORDER BY distance ASC  -- 余弦距离越小越相似
        LIMIT {top_k}
        """, (sqlite_vec.serialize_float32(query_embedding),))  # 同样需要序列化
        
        # 获取结果
        results = self.cursor.fetchall()
        # 格式化输出 - 距离转相似度
        formatted_results = [
            {
                "id": res[0],
                "content": res[1],
                "cosine_similarity": 1 - res[2]  # 余弦距离转相似度
            }
            for res in results
        ]
        return formatted_results

    # -------------------------- 5. 关闭连接 --------------------------
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        print("数据库连接已关闭")
