"""
多模态融合模块：整合不同检索源的结果
"""
from typing import List, Dict, Set
import re

class MultiModalFusion:
    def __init__(self):
        self.similarity_threshold = 0.7
        
    def fuse_results(self, vdb_results: List[str], sql_results: List[str], 
                    graph_results: List[str], query: str) -> List[str]:
        """融合多模态检索结果"""
        all_results = []
        
        # 标记来源
        for result in vdb_results:
            all_results.append({'content': result, 'source': 'vdb', 'score': 1.0})
        for result in sql_results:
            all_results.append({'content': result, 'source': 'sql', 'score': 1.0})
        for result in graph_results:
            all_results.append({'content': result, 'source': 'graph', 'score': 1.0})
        
        # 去重
        deduplicated = self._semantic_deduplication(all_results)
        
        # 互补性分析
        complementary = self._analyze_complementarity(deduplicated, query)
        
        # 重排序
        final_results = self._cross_modal_rerank(complementary, query)
        
        return [item['content'] for item in final_results]
    
    def _semantic_deduplication(self, results: List[Dict]) -> List[Dict]:
        """语义去重"""
        unique_results = []
        seen_contents: Set[str] = set()
        
        for result in results:
            content = result['content']
            
            # 简单文本去重
            normalized = re.sub(r'\s+', ' ', content.lower().strip())
            
            if normalized not in seen_contents:
                seen_contents.add(normalized)
                unique_results.append(result)
        
        return unique_results
    
    def _analyze_complementarity(self, results: List[Dict], query: str) -> List[Dict]:
        """分析结果互补性"""
        query_keywords = set(re.findall(r'\w+', query.lower()))
        
        for result in results:
            content_keywords = set(re.findall(r'\w+', result['content'].lower()))
            
            # 计算覆盖度
            coverage = len(query_keywords & content_keywords) / len(query_keywords) if query_keywords else 0
            
            # 信息密度
            info_density = len(re.findall(r'\d+|[A-Z][a-z]+', result['content']))
            
            # 来源权重
            source_weight = {'vdb': 1.0, 'sql': 1.2, 'graph': 1.1}[result['source']]
            
            # 综合评分
            result['fusion_score'] = coverage * 0.4 + (info_density / 10) * 0.3 + source_weight * 0.3
        
        return results
    
    def _cross_modal_rerank(self, results: List[Dict], query: str) -> List[Dict]:
        """跨模态重排序"""
        # 按融合分数排序
        ranked = sorted(results, key=lambda x: x['fusion_score'], reverse=True)
        
        # 确保多样性：不同来源的结果交替出现
        final_results = []
        sources_used = []
        
        for result in ranked:
            if len(final_results) < 3:  # 前3个结果保证质量
                final_results.append(result)
                sources_used.append(result['source'])
            else:
                # 后续结果考虑多样性
                if result['source'] not in sources_used[-2:]:  # 避免连续相同来源
                    final_results.append(result)
                    sources_used.append(result['source'])
        
        return final_results[:8]  # 限制总数量

class ResultDeduplicator:
    """结果去重器"""
    
    def __init__(self, similarity_threshold=0.8):
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, results: List[str]) -> List[str]:
        """去除重复和高度相似的结果"""
        if not results:
            return []
        
        unique_results = [results[0]]  # 保留第一个
        
        for result in results[1:]:
            is_duplicate = False
            
            for existing in unique_results:
                if self._is_similar(result, existing):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def _is_similar(self, text1: str, text2: str) -> bool:
        """判断两个文本是否相似"""
        # 简单的相似度计算
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        jaccard_similarity = intersection / union if union > 0 else 0
        
        return jaccard_similarity > self.similarity_threshold