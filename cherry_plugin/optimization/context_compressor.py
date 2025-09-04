"""
上下文压缩模块：智能压缩检索结果，避免token溢出
"""
import re
from typing import List, Dict

class ContextCompressor:
    def __init__(self, max_tokens=2000):
        self.max_tokens = max_tokens
        
    def compress_context(self, retrieved_items: List[str], query: str) -> List[str]:
        """智能压缩上下文"""
        if not retrieved_items:
            return []
            
        current_tokens = self._estimate_tokens(retrieved_items)
        
        if current_tokens <= self.max_tokens:
            return retrieved_items
            
        scored_items = self._score_importance(retrieved_items, query)
        return self._dynamic_compress(scored_items, self.max_tokens)
    
    def _estimate_tokens(self, texts: List[str]) -> int:
        """估算token数量"""
        total_chars = sum(len(text) for text in texts)
        return total_chars // 4
    
    def _score_importance(self, items: List[str], query: str) -> List[Dict]:
        """为检索项评分"""
        scored_items = []
        query_keywords = set(re.findall(r'\w+', query.lower()))
        
        for item in items:
            score = 0
            item_keywords = set(re.findall(r'\w+', item.lower()))
            
            # 关键词匹配
            keyword_overlap = len(query_keywords & item_keywords)
            score += keyword_overlap * 10
            
            # 长度惩罚
            length_penalty = min(len(item) / 200, 2)
            score -= length_penalty
            
            scored_items.append({
                'content': item,
                'score': score,
                'tokens': len(item) // 4
            })
        
        return sorted(scored_items, key=lambda x: x['score'], reverse=True)
    
    def _dynamic_compress(self, scored_items: List[Dict], max_tokens: int) -> List[str]:
        """动态压缩"""
        result = []
        used_tokens = 0
        
        for item in scored_items:
            if used_tokens + item['tokens'] <= max_tokens:
                result.append(item['content'])
                used_tokens += item['tokens']
            elif used_tokens < max_tokens * 0.8:
                compressed = self._summarize_content(item['content'], max_tokens - used_tokens)
                if compressed:
                    result.append(f"[摘要] {compressed}")
                break
        
        return result
    
    def _summarize_content(self, content: str, max_tokens: int) -> str:
        """内容摘要"""
        max_chars = max_tokens * 4
        if len(content) <= max_chars:
            return content
        return content[:max_chars-3] + "..."