import os
from openai import OpenAI


class LLM:
    """
    LLM 调用类（OpenAI 兼容接口）
    支持 Kimi / Qwen / DeepSeek 等模型
    
    ⚠️ 安全提示：
    - API Key 应从环境变量读取，不要硬编码
    - 创建 .env 文件存储：MOONSHOT_API_KEY=sk-xxx
    - .env 文件已加入 .gitignore，不会提交到 Git
    """
    
    def __init__(self, api_key: str = None):
        """
        初始化 LLM 客户端
        
        Args:
            api_key: API Key（可选，默认从环境变量读取）
        """
        # 优先使用传入的 API Key，其次从环境变量读取
        self.api_key = api_key or os.getenv('MOONSHOT_API_KEY', '')
        if not self.api_key:
            print("⚠️ 警告：未设置 API Key，请在 .env 文件中配置 MOONSHOT_API_KEY")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.cn/v1",  # Kimi API
            # 或者使用其他兼容接口：
            # base_url="https://api.openai.com/v1",  # OpenAI
            # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # Qwen
        )
    
    def chat(self, query: str) -> str:
        """
        发送聊天请求
        
        Args:
            query: 用户问题
        
        Returns:
            LLM 回答文本
        """
        try:
            completion = self.client.chat.completions.create(
                model="kimi-k2-turbo-preview",  # 可配置
                messages=[
                    {
                        "role": "system",
                        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手。你会为用户提供安全、有帮助、准确的回答。"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.6,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"❌ LLM 调用失败：{str(e)}"


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 方式 1：从环境变量读取（推荐）
    # 在 .env 文件中设置：MOONSHOT_API_KEY=sk-xxx
    llm = LLM()
    
    # 方式 2：直接传入 API Key（不推荐，仅用于测试）
    # llm = LLM(api_key="sk-your-key-here")
    
    response = llm.chat("你好，请介绍一下自己")
    print(response)
