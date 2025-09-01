"""
向量检索模块：FAISS向量数据库
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class VectorDB:
    def __init__(self, model_name=None):
        # 优先使用中文优化模型（强制CPU）
        device = 'cpu'  # 强制使用CPU
        if model_name is None:
            try:
                self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
                self.dimension = 384
            except:
                self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)
                self.dimension = 384
        else:
            self.model = SentenceTransformer(model_name, device=device)
            self.dimension = 384  # 默认维度
        
        self.index = None
        self.documents = []
        
    def add_documents(self, docs):
        """添加文档到向量数据库"""
        if not docs:
            return
            
        # 生成embeddings
        embeddings = self.model.encode(docs)
        
        # 初始化FAISS索引
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # 内积相似度
            
        # 标准化向量（用于余弦相似度）
        faiss.normalize_L2(embeddings)
        
        # 添加到索引
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(docs)
        
        print(f"已添加 {len(docs)} 个文档，总计 {len(self.documents)} 个文档")
    
    def search(self, query, k=5, use_rerank=True):
        """搜索相似文档"""
        if self.index is None or len(self.documents) == 0:
            return []
            
        # 生成查询向量
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # 搜索更多候选用于重排序
        search_k = min(k * 4, len(self.documents)) if use_rerank else min(k, len(self.documents))
        scores, indices = self.index.search(query_embedding.astype('float32'), search_k)
        
        # 返回结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'score': float(score)
                })
        
        # 重排序
        if use_rerank and len(results) > k:
            from .reranker import VectorReranker
            reranker = VectorReranker(self.model)
            results = reranker.rerank_vector_results(query, results, k)
        
        return results[:k]
    
    def save(self, path):
        """保存向量数据库"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 保存FAISS索引
        if self.index is not None:
            faiss.write_index(self.index, f"{path}.index")
        
        # 保存文档
        with open(f"{path}.docs", 'wb') as f:
            pickle.dump(self.documents, f)
            
        print(f"向量数据库已保存到 {path}")
    
    def load(self, path):
        """加载向量数据库"""
        try:
            # 加载FAISS索引
            if os.path.exists(f"{path}.index"):
                self.index = faiss.read_index(f"{path}.index")
            
            # 加载文档
            if os.path.exists(f"{path}.docs"):
                with open(f"{path}.docs", 'rb') as f:
                    self.documents = pickle.load(f)
                    
            print(f"向量数据库已从 {path} 加载，包含 {len(self.documents)} 个文档")
            return True
        except Exception as e:
            print(f"加载向量数据库失败: {e}")
            return False