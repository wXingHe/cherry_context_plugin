"""
向量检索模块：FAISS向量数据库
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class VectorDB:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.dimension = 384  # all-MiniLM-L6-v2的维度
        
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
    
    def search(self, query, k=5):
        """搜索相似文档"""
        if self.index is None or len(self.documents) == 0:
            return []
            
        # 生成查询向量
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # 搜索
        scores, indices = self.index.search(query_embedding.astype('float32'), min(k, len(self.documents)))
        
        # 返回结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'score': float(score)
                })
        
        return results
    
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