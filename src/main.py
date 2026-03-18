from RAG import *
import os
from dotenv import load_dotenv

# 加载 .env 文件（从项目根目录）
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

def get_abs_path(relative_path):
    """
    获取相对于当前代码文件的绝对路径
    :param relative_path: 相对于当前文件的路径
    :return: 绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def main():
    
    db_path = get_abs_path('../sqlight/vec_2.db') # 这个是你要创建的向量数据库的路径
    rag = RAG(db_path) 
    knowledge_path = get_abs_path('../knowledge_base') # 这个是你的文件路径
    print(knowledge_path)
    rag.init_vec_db(knowledge_path = knowledge_path) # 这个是初始化的代码，当初始化了之后可以不用
    print(rag.retrieval_augmented_generate('计算机与信息安全学院推免研究生的学业成绩要求是什么？'))


if __name__ == "__main__":
    main()

