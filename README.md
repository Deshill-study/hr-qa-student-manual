# HR 智能助手 - 学生手册问答系统

基于 RAG（检索增强生成）技术的高校学生手册智能问答系统，支持私有化部署。

## 🌟 功能特性

- 🤖 **智能问答**：基于 RAG 技术，准确回答学生手册相关问题
- 📚 **知识库管理**：支持 PDF/Markdown 格式文档，自动分块索引
- 🔒 **私有化部署**：数据本地存储，Embedding 模型本地运行
- 💬 **Web 界面**：基于 Gradio 的友好交互界面
- ⚡ **轻量级**：基于 SQLite-Vec 向量库，无需额外数据库依赖

## 🏗️ 技术架构

### 技术栈

| 模块 | 技术选型 |
|------|----------|
| RAG 框架 | 自研 RAG 引擎 |
| 向量数据库 | SQLite + sqlite-vec |
| Embedding 模型 | nomic-embed-text-v1.5 (768 维) |
| LLM | Kimi / Qwen / DeepSeek（可配置） |
| 前端界面 | Gradio |
| 部署环境 | Linux + Python 3.10+ |

### 核心模块

```
src/
├── RAG/
│   ├── text_process/       # 文本处理模块
│   │   ├── document_loader.py   # 文档加载（PDF/Markdown）
│   │   └── text_chunker.py      # 智能分块（段落 + 语义边界）
│   ├── build_index/        # 索引构建模块
│   │   ├── embedding.py         # Embedding 生成（llama.cpp）
│   │   └── index_storage.py     # 向量存储（SQLite-Vec）
│   ├── llm_generate/       # LLM 生成模块
│   │   └── llm.py               # LLM 调用（OpenAI 兼容接口）
│   ├── retrieve/           # 检索模块（改进版）
│   │   └── retriever.py         # 混合检索 + RRF 融合 + 重排序
│   ├── rag.py              # RAG 主类
│   └── __init__.py
├── app.py                  # Gradio Web 界面
└── main.py                 # 命令行入口
```

## 🔬 核心技术

### 1️⃣ 智能文本分块策略

**问题**：传统固定长度分块容易切断语义完整的段落。

**解决方案**：段落 + 语义边界分块

```python
# 按段落优先分块
paragraphs = text.split('\n\n')

# 长段落递归切分，优先在句子边界切断
separators = ['。\n', '.\n', '；', ',', ' ']  # 按优先级尝试

# 参数优化
chunk_size = 1000-1500  # 每块最大字符数
overlap = 150-200       # 相邻块重叠，保持上下文连贯
```

**效果**：
- ✅ 保持段落完整性
- ✅ 避免在概念中间切断
- ✅ 重叠区域保证检索连贯性

### 2️⃣ 混合检索架构

**传统 RAG**：仅向量检索 → top3 准确率 ~40%

**改进架构**：

```
用户查询
    │
    ├─→ 向量检索 (20 个) ───┐
    │                       │
    └─→ 关键词检索 (20 个) ─┼─→ RRF 融合 (15 个) ─→ LLM 重排序 ─→ 最终结果 (7 个)
                            │
                            └─→ 互补优势
```

**技术细节**：

| 步骤 | 方法 | 作用 |
|------|------|------|
| 向量检索 | SQLite-Vec + 余弦相似度 | 捕捉语义相似性 |
| 关键词检索 | jieba 分词 + Jaccard 相似度 | 精确术语匹配 |
| RRF 融合 | `1/(60+rank_vector) + 1/(60+rank_keyword)` | 平衡两个系统 |
| LLM 重排序 | 相关性打分（0-10 分） | 最终精度优化 |

**RRF 融合公式**：
```python
RRF_score = 1/(60 + vector_rank) + 1/(60 + keyword_rank)
```

**效果对比**：

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| top3 准确率 | ~40% | ~65% | **+25%** |
| top7 准确率 | ~60% | ~85% | **+25%** |

### 3️⃣ LLM 重排序

对 RRF 融合后的 15 个候选文档，用 LLM 进行相关性打分：

```python
prompt = f"""请判断以下文档与查询的相关性，打分 0-10 分：

查询：{query}
文档：{content[:800]}

评分标准：
- 0-2 分：完全无关
- 3-5 分：部分相关
- 6-8 分：大部分相关
- 9-10 分：完全相关

只返回一个数字（0-10）："""
```

**优势**：
- ✅ 可解释性强（可输出打分理由）
- ✅ 准确率高（LLM 理解语义）
- ✅ 可配置开关（平衡性能和速度）

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Linux / macOS（Windows 需调整部分配置）
- 4GB+ 内存（Embedding 模型需要）

### 2. 安装依赖

```bash
# 基础依赖
conda create -n hr python=3.12
pip install -r requirements.txt

# llama.cpp（用于本地 Embedding）
pip install llama-cpp-python

# 或者使用预编译版本
CMAKE_ARGS="-DLLAMA_BLAS=ON" pip install llama-cpp-python
```

### 3. 配置 API Key

创建 `.env` 文件:

```bash
# Kimi API
MOONSHOT_API_KEY=sk-your-api-key-here

# 或者使用其他 LLM
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 4. 准备知识库

将学生手册文档放入 `knowledge_base/` 目录：

```bash
knowledge_base/
├── md/
│   └── 学生手册.md
└── pdf/
    └── 学生手册.pdf
```

### 5. 构建索引

```bash
cd src
python main.py
```

首次运行会自动：
1. 读取知识库文档
2. 智能分块
3. 生成 Embedding
4. 存储到 SQLite-Vec

### 6. 启动 Web 界面

```bash
python app.py
```

访问 `http://localhost:7860` 即可使用。

## 📊 使用示例
### Web 界面

启动后自动打开 Gradio 界面，支持：
- ❓ 自然语言提问
- 📊 可调节检索文档数量（top_k）
- 📚 显示参考来源和相似度分数
- 💡 示例问题快捷输入


## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 回答准确率（top3） | ~65% |
| 回答准确率（top7） | ~85% |
| 平均响应时间 | 2-5s（含 LLM 生成） |
| 索引构建速度 | ~10 文档/秒 |
| 支持文档格式 | PDF, Markdown, TXT |
| 向量维度 | 768 |

## 🔧 配置说明

### Embedding 模型配置

编辑 `src/RAG/build_index/embedding.py`：

```python
model_path = "/path/to/nomic-embed-text-v1.5.Q8_0.gguf"  # 修改为你的模型路径
n_ctx = 512          # 上下文长度
n_threads = 4        # 线程数
```

### LLM 配置

编辑 `src/RAG/llm_generate/llm.py`：

```python
# 从环境变量读取 API Key（推荐）
import os
api_key = os.getenv('MOONSHOT_API_KEY', 'sk-your-key-here')

# 或者修改模型
model = "kimi-k2-turbo-preview"  # 或 "qwen-plus", "deepseek-v3"
```

### 检索参数调优

```python
# RAG 检索
contexts = rag.retrieve_for_query(query, top_k=7)  # 调整检索数量

# 分块参数
chunker = TextChunker(chunk_size=1000, overlap=150)
```

## ️ 常见问题

### Q: Embedding 模型下载

nomic-embed-text 模型可从以下地址下载：
- HuggingFace: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF
- ModelScope: https://modelscope.cn/models/nomic-ai/nomic-embed-text-v1.5-GGUF

推荐下载 `Q8_0` 量化版本（约 300MB）。

### Q: 检索准确率不高

1. 检查 chunk_size 是否合适（推荐 1000-1500）
2. 增加 top_k 数量（5-7 个）
3. 启用 LLM 重排序
4. 优化知识库文档质量

### Q: 响应速度慢

1. 减少 top_k 数量
2. 关闭 LLM 重排序（`use_rerank=False`）
3. 使用更快的 LLM API
4. 增加 n_threads 线程数

### Q: SQLite-Vec 报错

确保已正确安装：
```bash
pip install sqlite-vec
```

如遇编译问题，参考官方文档：https://sqlite-vec.org/

## 📝 项目结构说明

```
hr-assistant/
├── src/                        # 核心代码
│   ├── RAG/
│   │   ├── text_process/       # 文本处理
│   │   │   ├── document_loader.py   # PDF/Markdown 加载
│   │   │   └── text_chunker.py      # 智能分块
│   │   ├── build_index/        # 索引构建
│   │   │   ├── embedding.py         # Embedding 生成
│   │   │   └── index_storage.py     # 向量存储
│   │   ├── llm_generate/       # LLM 生成
│   │   │   └── llm.py               # LLM 调用
│   │   ├── retrieve/           # 检索（改进版）
│   │   │   └── retriever.py         # 混合检索 + 重排序
│   │   ├── rag.py              # RAG 主类
│   │   └── __init__.py
│   ├── app.py                  # Gradio 界面
│   ├── main.py                 # 命令行入口
│   └── test/                   # 测试文件
├── knowledge_base/             # 知识库（.gitignore 忽略）
│   ├── md/
│   └── pdf/
├── sqlight/                    # 向量数据库（.gitignore 忽略）
├── reports/                    # 测试报告（.gitignore 忽略）
├── .env                        # 环境配置（.gitignore 忽略）
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔐 安全建议

1. **API Key 管理**：使用环境变量，不要硬编码
2. **知识库版权**：避免上传受版权保护的文档到公开仓库
3. **数据隐私**：学生手册等内部文档建议本地部署
4. **访问控制**：生产环境建议添加身份验证

## 🚧 后续优化方向

### 短期
- [ ] 父子分块（Parent-Child Chunking）
- [ ] 查询改写（Query Rewriting）
- [ ] 元数据过滤（按文档类型、日期）

### 中期
- [ ] 微调 Embedding 模型（领域适配）
- [ ] RAGAS 评估框架
- [ ] 多轮对话记忆

### 长期
- [ ] 端到端 RAG 优化
- [ ] Agent 自主检索决策
- [ ] 多模态 RAG（图表 + 文本）

## 📄 License

MIT License

## 👨‍💻 作者

Deshill

## 联系方式
1194334798@qq.com

## 🙏 致谢

- [SQLite-Vec](https://sqlite-vec.org/) - 轻量级向量数据库
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - 本地 LLM 推理
- [Gradio](https://gradio.app/) - 快速 Web 界面
- [Moonshot AI](https://www.moonshot.cn/) - Kimi LLM 服务

---

**注意**：本项目仅供学习交流使用，请勿用于商业用途。学生手册等文档版权归原学校所有。
