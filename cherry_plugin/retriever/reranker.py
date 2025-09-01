"""
重排序模块：提升向量检索精度
"""
import numpy as np
from typing import List, Tuple

class Reranker:
    def __init__(self, method="cosine"):
        self.method = method
        self.rerank_model = None
        
        if method == "bge":
            try:
                from FlagEmbedding import FlagReranker
                import os
                os.environ['CUDA_VISIBLE_DEVICES'] = ''  # 强制使用CPU
                self.rerank_model = FlagReranker('BAAI/bge-reranker-base', use_fp16=False)
            except ImportError:
                print("FlagEmbedding未安装，回退到余弦相似度重排序")
                self.method = "cosine"
    
    def rerank(self, query: str, docs: List[str], scores: List[float] = None, top_k: int = 5) -> List[Tuple[str, float]]:
        """重排序文档"""
        if not docs:
            return []
            
        if self.method == "bge" and self.rerank_model:
            return self._bge_rerank(query, docs, top_k)
        else:
            return self._cosine_rerank(query, docs, scores, top_k)
    
    def _bge_rerank(self, query: str, docs: List[str], top_k: int) -> List[Tuple[str, float]]:
        """BGE重排序"""
        try:
            pairs = [[query, doc] for doc in docs]
            scores = self.rerank_model.compute_score(pairs)
            
            # 确保scores是列表
            if not isinstance(scores, list):
                scores = [scores]
                
            # 排序并返回top_k
            ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
            return ranked[:top_k]
            
        except Exception as e:
            print(f"BGE重排序失败: {e}")
            return [(doc, 0.0) for doc in docs[:top_k]]
    
    def _cosine_rerank(self, query: str, docs: List[str], scores: List[float], top_k: int) -> List[Tuple[str, float]]:
        """余弦相似度重排序"""
        if scores:
            # 使用原始分数排序
            ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
            return ranked[:top_k]
        else:
            # 简单返回前top_k个
            return [(doc, 1.0) for doc in docs[:top_k]]

class VectorReranker:
    """向量检索专用重排序器"""
    
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model
        self.reranker = Reranker("bge")
    
    def rerank_vector_results(self, query: str, results: List[dict], top_k: int = 5) -> List[dict]:
        """重排序向量检索结果"""
        if not results:
            return []
        
        # 提取文档和分数
        docs = [r['document'] for r in results]
        scores = [r['score'] for r in results]
        
        # 重排序
        reranked = self.reranker.rerank(query, docs, scores, top_k)
        
        # 重构结果格式
        reranked_results = []
        for doc, score in reranked:
            reranked_results.append({
                'document': doc,
                'score': float(score),
                'reranked': True
            })
        
        return reranked_results