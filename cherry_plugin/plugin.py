"""
Cherry Studio 上下文插件主入口
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cherry_plugin.routing.hybrid_route import HybridRouter
from cherry_plugin.retriever.vector_db import VectorDB
from cherry_plugin.retriever.sql_db import SqlDB
from cherry_plugin.retriever.graph_db import GraphDB
from cherry_plugin.memory.memory_store import MemoryStore
from cherry_plugin.prompt_template import PromptTemplate
from cherry_plugin.cache import CacheManager

class CherryContextPlugin:
    def __init__(self):
        # 初始化各个模块
        self.router = HybridRouter()
        self.vector_db = VectorDB()
        self.sql_db = SqlDB()
        # 使用绝对路径初始化图数据库
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        graph_path = os.path.join(base_dir, "cherry_plugin/data/graph_data.json")
        self.graph_db = GraphDB(graph_path)
        self.memory = MemoryStore()
        self.prompt_template = PromptTemplate()
        self.cache = CacheManager()
        
        # 加载向量数据库
        vector_path = os.path.join(base_dir, "cherry_plugin/data/vector_db")
        self.vector_db.load(vector_path)
        

        
        print("Cherry上下文插件初始化完成")
    
    def build_prompt(self, short_term, retrieved, long_term, user_question):
        """构建最终的prompt"""
        prompt_parts = ["系统指令: 你是智能中文助手。"]
        
        if short_term:
            prompt_parts.append(f"短期对话记忆:\n{short_term}")
        
        if retrieved:
            retrieved_text = "\n".join([str(item) for item in retrieved])
            prompt_parts.append(f"相关知识检索结果:\n{retrieved_text}")
        
        if long_term:
            prompt_parts.append(f"长期摘要:\n{long_term}")
        
        prompt_parts.append(f"用户问题:\n{user_question}")
        
        return "\n\n".join(prompt_parts)
    
    def process_question(self, user_question):
        """处理用户问题的主流程"""
        print(f"\n=== 处理问题: {user_question} ===")
        
        # 1. 获取记忆
        short_term = self.memory.get_short_term_context(max_turns=3)
        long_term = self.memory.get_long_term_summary()
        
        # 2. 动态路由
        route, scores = self.router.route(user_question)
        print(f"路由结果: {route}")
        
        # 3. 检索相关信息
        retrieved = []
        
        if route == "vdb":
            # 向量检索（启用重排序）
            vdb_results = self.vector_db.search(user_question, k=3, use_rerank=True)
            retrieved = [f"文档: {r['document']} (分数: {r['score']:.3f}{'*' if r.get('reranked') else ''})" 
                        for r in vdb_results]
            
        elif route == "sql":
            # SQL检索
            sql_results = self.sql_db.search(user_question, limit=3)
            for result in sql_results:
                if result['type'] == 'config':
                    retrieved.append(f"配置: {result['key']} = {result['value']} ({result['description']})")
                else:
                    retrieved.append(f"规则: {result['name']} - {result['condition']} -> {result['action']}")
        
        elif route == "graph":
            # 图检索
            cached_result = self.cache.get(user_question, "graph")
            if cached_result is not None and len(cached_result) > 0:
                retrieved = cached_result
            else:
                graph_results = self.graph_db.search_relationships(user_question, limit=5)
                # 去重处理
                unique_results = []
                seen = set()
                for r in graph_results:
                    key = f"{r['from']['id']}-{r['relationship']}-{r['to']['id']}"
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(r)
                
                retrieved = [f"关系: {r['from']['id']}({r['from']['properties'].get('职位', '')}) -[{r['relationship']}]-> {r['to']['id']}({r['to']['properties'].get('职位', '')})" 
                           for r in unique_results[:3]]
                if retrieved:
                    self.cache.set(user_question, "graph", retrieved)
        
        # 4. 多模态融合与上下文压缩
        from .optimization.multimodal_fusion import MultiModalFusion
        from .optimization.context_compressor import ContextCompressor
        
        # 融合不同源的结果
        fusion = MultiModalFusion()
        vdb_items = retrieved if route == "vdb" else []
        sql_items = retrieved if route == "sql" else []
        graph_items = retrieved if route == "graph" else []
        
        fused_results = fusion.fuse_results(vdb_items, sql_items, graph_items, user_question)
        
        # 压缩上下文
        compressor = ContextCompressor(max_tokens=1500)
        compressed_results = compressor.compress_context(fused_results, user_question)
        
        # 5. 构建最终prompt
        final_prompt = self.prompt_template.generate_prompt(
            user_question, short_term, compressed_results, long_term, 
            template_type="with_memory" if short_term else "default"
        )
        final_prompt = self.prompt_template.optimize_prompt_length(final_prompt)
        
        # 更新retrieved为压缩后的结果
        retrieved = compressed_results
        
        return {
            "route": route,
            "route_scores": scores,
            "retrieved": retrieved,
            "short_term": short_term,
            "long_term": long_term,
            "final_prompt": final_prompt
        }
    
    def add_conversation(self, user_input, assistant_response):
        """添加对话到记忆"""
        self.memory.add_conversation(user_input, assistant_response)
    
    def add_documents(self, documents):
        """添加文档到向量数据库"""
        self.vector_db.add_documents(documents)
        self.vector_db.save("cherry_plugin/data/vector_db")
    
    def add_config(self, key, value, description="", category="general"):
        """添加配置到SQL数据库"""
        self.sql_db.add_config(key, value, description, category)

# Cherry Studio插件接口函数
def cherry_pipeline(user_question):
    """Cherry Studio调用的主函数"""
    plugin = CherryContextPlugin()
    result = plugin.process_question(user_question)
    return result["final_prompt"]