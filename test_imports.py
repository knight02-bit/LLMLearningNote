# 测试 LlamaIndex 导入是否正常工作
print("开始测试导入...")

# 测试核心模块导入
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
    print("✓ 成功导入 llama_index.core 模块")
except ImportError as e:
    print(f"✗ 导入 llama_index.core 失败: {e}")

# 测试向量存储导入
try:
    from llama_index.vector_stores.chroma import ChromaVectorStore
    print("✓ 成功导入 llama_index.vector_stores.chroma 模块")
except ImportError as e:
    print(f"✗ 导入 llama_index.vector_stores.chroma 失败: {e}")

# 测试嵌入模型导入
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    print("✓ 成功导入 llama_index.embeddings.huggingface 模块")
except ImportError as e:
    print(f"✗ 导入 llama_index.embeddings.huggingface 失败: {e}")

# 测试 chromadb 导入
try:
    import chromadb
    print("✓ 成功导入 chromadb 模块")
except ImportError as e:
    print(f"✗ 导入 chromadb 失败: {e}")

print("\n导入测试完成!")
