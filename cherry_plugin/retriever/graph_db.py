"""
图数据库检索模块：Neo4j知识图谱（简化版本）
"""
import json
import os

class GraphDB:
    def __init__(self, data_path="cherry_plugin/data/graph_data.json"):
        self.data_path = data_path
        self.graph_data = {"nodes": [], "relationships": []}
        self.load_data()
    
    def add_node(self, node_id, label, properties=None):
        """添加节点"""
        node = {
            "id": node_id,
            "label": label,
            "properties": properties or {}
        }
        self.graph_data["nodes"].append(node)
        self.save_data()
    
    def add_relationship(self, from_id, to_id, relation_type, properties=None):
        """添加关系"""
        relationship = {
            "from": from_id,
            "to": to_id,
            "type": relation_type,
            "properties": properties or {}
        }
        self.graph_data["relationships"].append(relationship)
        self.save_data()
    
    def search_relationships(self, query, limit=5):
        """搜索关系"""
        results = []
        query_lower = query.lower()
        
        # 提取关键词（简单的中文分词）
        keywords = []
        # 常见人名模式
        import re
        chinese_names = re.findall(r'[一-鿿]{2,3}', query)
        keywords.extend(chinese_names)
        
        # 关系关键词
        relation_keywords = ['合作', '协作', '沟通', '负责', '参与']
        for keyword in relation_keywords:
            if keyword in query:
                keywords.append(keyword)
        

        
        # 搜索包含查询词的关系或节点
        for rel in self.graph_data["relationships"]:
            match_found = False
            
            # 检查关键词匹配
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # 检查关系类型
                if keyword_lower in rel["type"].lower():
                    match_found = True
                
                # 检查节点ID
                if keyword_lower in rel["from"].lower() or keyword_lower in rel["to"].lower():
                    match_found = True
                    
                # 检查关系属性
                if any(keyword_lower in str(v).lower() for v in rel["properties"].values()):
                    match_found = True
                    
                # 检查节点属性
                from_node = self.get_node_by_id(rel["from"])
                to_node = self.get_node_by_id(rel["to"])
                
                if from_node and any(keyword_lower in str(v).lower() for v in from_node["properties"].values()):
                    match_found = True
                if to_node and any(keyword_lower in str(v).lower() for v in to_node["properties"].values()):
                    match_found = True
                    
                if match_found:
                    break
                    
            if match_found and from_node and to_node:
                results.append({
                    "from": from_node,
                    "to": to_node,
                    "relationship": rel["type"],
                    "properties": rel["properties"]
                })
        
        return results[:limit]
    
    def get_node_by_id(self, node_id):
        """根据ID获取节点（返回最后一个匹配的节点）"""
        matched_node = None
        for node in self.graph_data["nodes"]:
            if node["id"] == node_id:
                matched_node = node  # 保存最后一个匹配的节点
        return matched_node
    
    def save_data(self):
        """保存图数据"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph_data, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """加载图数据"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.graph_data = json.load(f)
            except Exception as e:
                print(f"加载图数据失败: {e}")
                self.graph_data = {"nodes": [], "relationships": []}