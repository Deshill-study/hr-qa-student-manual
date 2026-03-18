from RAG import *
import os
def get_abs_path(relative_path):
    """
    获取相对于当前代码文件的绝对路径
    :param relative_path: 相对于当前文件的路径
    :return: 绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def main():
    db_path = get_abs_path('../sqlight/vec_2.db')
    rag = RAG(db_path)
    knowledge_path = get_abs_path('../knowledge_base')
    print(knowledge_path)
    rag.init_vec_db(knowledge_path = knowledge_path)
    print(rag.retrieval_augmented_generate('计算机与信息安全学院志愿服务综合测评加分有几种方式？'))

import gradio as gr
# ============== 初始化组件 ==============
print("🔄 正在加载 RAG 检索器...")
db_path = get_abs_path('../sqlight/vec_3.db')
knowledge_path = get_abs_path('../knowledge_base')
rag = RAG(db_path)
#rag.init_vec_db(knowledge_path = knowledge_path)

print("🔄 正在加载 LLM 客户端...")

# ============== 核心功能 ==============
def answer_question(question, top_k=6):
    """
    回答用户问题
    
    Args:
        question: 用户问题
        top_k: 检索的文档数量
    
    Returns:
        answer: 回答文本
        sources: 引用来源列表
    """
    if not question.strip():
        return "⚠️ 请输入问题", []
    
    try:
        # 1. RAG 检索
        print(f"🔍 正在检索：{question}")
        contexts = rag.retrieve_for_query(question, top_k=top_k)
        
        if not contexts:
            return "❌ 抱歉，没有找到相关的资料。", []
        context_text = ''
        for i,doc in enumerate(contexts):
            context_text += f'资料{i+1}\n'
            context_text += f"{doc['content']}\n\n"

        # # 2. 组装 Prompt
        # context_text = "\n\n".join([
        #     f"[资料{i+1}]\n{c[0]}" 
        #     for i, c in enumerate(contexts)
        # ])
        print(context_text)
        prompt = f'你是 HR 智能助手，基于以下资料回答问题。'+f'{context_text}'+f'问题：{question}'+'请用简洁清晰的语言回答'

        
        # 3. LLM 生成答案
        print("🤖 正在生成答案...")
        #print(prompt)
        answer = rag.generate_answer(prompt)
        print(answer)
        # 4. 准备引用来源
        sources = [
            {
                "来源": f"资料{i+1}",
                "向量相似度": f"{c.get('cosine_similarity', c.get('vector_score', 0)):.2f}",
                "模型评价的相似度":f"{c['relevance_score']}",
                "内容": c['content'][:200] + "..."
            }
            for i, c in enumerate(contexts)
        ]
        print("✅ 完成！")
        return answer, sources
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return f"出错了：{str(e)}", []

# ============== 创建界面 ==============
with gr.Blocks(title="💼 HR 智能助手", theme=gr.themes.Soft()) as demo:
    # 标题
    gr.Markdown("""
    # 💼 HR 智能助手
    基于 RAG 的学生手册问答系统
    """)
    
    # 主布局
    with gr.Row():
        # 左侧：输入和输出
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="❓ 问题",
                placeholder="请输入你的问题，例如：宿舍管理规定是什么？",
                lines=3
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 提交", variant="primary")
                clear_btn = gr.Button("🗑️ 清空")
            
            answer_output = gr.Textbox(
                label="💬 回答",
                lines=6,
            )
            
            # 示例问题
            gr.Examples(
                examples=[
                    "宿舍管理规定是什么？",
                    "考试作弊怎么处理？",
                    "奖学金评定标准？",
                    "请假流程是怎样的？",
                    "毕业要求有哪些？"
                ],
                inputs=question_input
            )
        
        # 右侧：设置和来源
        with gr.Column(scale=2):
            top_k_slider = gr.Slider(
                minimum=1,
                maximum=10,
                value=3,
                step=1,
                label="📊 检索文档数量"
            )
            
            sources_output = gr.JSON(label="📚 参考来源")
    
    # 绑定事件
    submit_btn.click(
        fn=answer_question,
        inputs=[question_input, top_k_slider],
        outputs=[answer_output, sources_output],
        api_name="ask"
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=[],
        outputs=[question_input, answer_output]
    )

# ============== 启动服务 ==============
if __name__ == "__main__":
    print("\n" + "="*50)
    print("✅ 服务启动成功！")
    print("🌐 本地访问：http://localhost:7860")
    print("🌐 局域网访问：http://你的 IP:7860")
    print("="*50)
    print("\n按 Ctrl+C 停止服务\n")
    
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860
    )
