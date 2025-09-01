# 重排序优化指南

## 什么时候需要重排序？

### ✅ 需要重排序的场景

**向量数据库检索 (VDB)**
- 强烈建议启用，特别是中文语境
- 原因：纯向量相似度可能返回"看似相关但不精确"的结果
- 示例：查询"合作伙伴合同"可能检索到"合同模板"或"合作伙伴新闻"

### ❌ 不需要重排序的场景

**SQL/图数据库检索**
- 通常不需要，查询本身是精确的
- 示例：`SELECT * FROM configs WHERE key='api_limit'` → 结果唯一

## 重排序方案

### 方案A: BGE重排序 (推荐)

```python
# 自动启用，无需额外配置
vdb_results = vector_db.search("查询内容", k=5, use_rerank=True)
```

**特点:**
- 使用 `BAAI/bge-reranker-base` 模型
- 中文效果优秀
- CPU上延迟 20-100ms
- 自动回退到余弦相似度

### 方案B: 余弦相似度重排序

```python
# 轻量级方案，无需额外模型
vdb_results = vector_db.search("查询内容", k=5, use_rerank=False)
```

**特点:**
- 基于原始向量相似度
- 性能开销最小
- 适合资源受限环境

## 配置选项

### 启用/禁用重排序

```python
# 在插件配置中设置
{
  "retrieval": {
    "vector_rerank": true,        # 启用向量重排序
    "rerank_method": "bge",       # bge | cosine
    "rerank_top_k": 5,           # 重排序后返回数量
    "rerank_candidates": 20       # 重排序候选数量
  }
}
```

### 性能调优

```python
# 调整候选数量平衡精度和性能
search_k = k * 4  # 候选数量 = 目标数量 × 4
```

## 效果对比

### 测试查询: "Python机器学习教程"

**无重排序:**
1. Python基础语法 (0.85)
2. 机器学习概述 (0.82) 
3. 教程目录 (0.80)

**BGE重排序:**
1. Python机器学习实战教程 (0.92)
2. 机器学习Python库介绍 (0.89)
3. Python数据科学教程 (0.85)

## 安装重排序模型

### 自动安装
```bash
pip install FlagEmbedding>=1.2.0
```

### 手动下载模型
```python
from FlagEmbedding import FlagReranker

# 首次使用会自动下载
reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True)
```

### 离线部署
```bash
# 预下载模型
mkdir -p models/
cd models/
git clone https://huggingface.co/BAAI/bge-reranker-base

# 使用本地模型
reranker = FlagReranker('./models/bge-reranker-base', use_fp16=True)
```

## 性能监控

### 测试重排序效果
```python
from cherry_plugin.retriever.reranker import VectorReranker
import time

reranker = VectorReranker()
query = "Python机器学习教程"
docs = ["文档1", "文档2", "文档3"]

start = time.time()
results = reranker.rerank_vector_results(query, docs, top_k=3)
end = time.time()

print(f"重排序耗时: {end-start:.3f}秒")
for i, result in enumerate(results):
    print(f"{i+1}. {result['document']} (分数: {result['score']:.3f})")
```

### 性能基准
- **BGE重排序**: 20-100ms (CPU)
- **余弦重排序**: 1-5ms
- **内存占用**: +200MB (BGE模型)

## 故障排除

### FlagEmbedding安装失败
```bash
# 使用国内镜像
pip install FlagEmbedding -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或禁用重排序
use_rerank=False
```

### 内存不足
```python
# 使用FP16精度
FlagReranker('BAAI/bge-reranker-base', use_fp16=True)

# 或减少候选数量
search_k = k * 2  # 减少到2倍
```

### 中文效果不佳
```python
# 确保使用中文优化模型
reranker = FlagReranker('BAAI/bge-reranker-base')  # 支持中文
```

## 最佳实践

1. **向量检索必开**: 显著提升检索精度
2. **候选数量**: 目标数量的3-4倍效果最佳
3. **性能平衡**: 实时场景用余弦，高质量场景用BGE
4. **缓存结果**: 相同查询缓存重排序结果
5. **监控延迟**: 确保总延迟在可接受范围内