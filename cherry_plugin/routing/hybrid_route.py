"""
混合路由模块：Embedding + 本地LLM分类
"""
from sentence_transformers import SentenceTransformer, util
import requests
import json

class HybridRouter:
    def __init__(self):
        # 优先使用中文优化模型（强制CPU）
        import torch
        device = 'cpu'  # 强制使用CPU
        try:
            self.embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
        except:
            self.embed_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)
        self.module_examples = {
            "vdb": ["查找文档内容", "历史对话查询", "笔记检索", "搜索相关资料", "Python教程", "机器学习资料"],
            "sql": ["查询配置参数", "API接口限制", "系统设置", "数据库规则", "限制是多少", "参数配置"],
            "graph": ["谁是张三的合作者", "上下游关系", "知识图谱查询", "关系网络", "合作伙伴"]
        }
        self.module_emb = {k: self.embed_model.encode(v) for k, v in self.module_examples.items()}
    
    def embedding_route(self, question):
        """Embedding初筛"""
        q_emb = self.embed_model.encode([question])
        scores = {}
        for module, examples_emb in self.module_emb.items():
            similarities = util.cos_sim(q_emb, examples_emb)
            scores[module] = float(similarities.max())
        
        best_route = max(scores, key=scores.get)
        return best_route, scores
    
    def llm_route(self, question):
        """LLM精筛"""
        prompt = f"""你是一个分类器，请只输出 vdb/sql/graph 中的一个。
- vdb: 文档、笔记、对话类查询
- sql: 参数、配置、规则表类查询  
- graph: 上下游关系、合作者关系类查询

问题: {question}
分类:"""
        
        try:
            response = requests.post("http://localhost:11434/api/generate", 
                json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False},
                timeout=10)
            result = response.json()["response"].strip().lower()
            
            # 提取有效分类
            for route in ["vdb", "sql", "graph"]:
                if route in result:
                    return route
            return "vdb"  # 默认返回vdb
            
        except Exception as e:
            print(f"LLM路由失败: {e}")
            return "vdb"
    
    def route(self, question, threshold=0.1):
        """混合路由决策"""
        embed_route, scores = self.embedding_route(question)
        
        # 计算分数差异
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        score_diff = sorted_scores[0][1] - sorted_scores[1][1]
        
        # 如果分数差异小于阈值，使用LLM精筛
        if score_diff < threshold:
            final_route = self.llm_route(question)
            print(f"使用LLM路由: {question} -> {final_route}")
        else:
            final_route = embed_route
            print(f"使用Embedding路由: {question} -> {final_route}")
        
        return final_route, scores