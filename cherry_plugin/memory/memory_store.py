"""
记忆存储模块：短期记忆和长期摘要
"""
import json
import os
from datetime import datetime, timedelta
from collections import deque

class MemoryStore:
    def __init__(self, data_dir="cherry_plugin/data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.short_term_file = os.path.join(data_dir, "short_term_memory.json")
        self.long_term_file = os.path.join(data_dir, "long_term_summary.json")
        
        # 短期记忆设置
        self.max_short_term = 10  # 最多保存10轮对话
        self.short_term_memory = deque(maxlen=self.max_short_term)
        
        # 长期摘要
        self.long_term_summary = ""
        
        self.load_memory()
    
    def add_conversation(self, user_input, assistant_response):
        """添加对话到短期记忆"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response
        }
        
        self.short_term_memory.append(conversation)
        self.save_short_term()
        
        # 如果短期记忆满了，更新长期摘要
        if len(self.short_term_memory) >= self.max_short_term:
            self.update_long_term_summary()
    
    def get_short_term_context(self, max_turns=5):
        """获取短期对话上下文"""
        recent_conversations = list(self.short_term_memory)[-max_turns:]
        
        context = []
        for conv in recent_conversations:
            context.append(f"用户: {conv['user']}")
            context.append(f"助手: {conv['assistant']}")
        
        return "\n".join(context)
    
    def update_long_term_summary(self):
        """更新长期摘要（简化版本）"""
        if not self.short_term_memory:
            return
        
        # 提取关键主题（简化实现）
        topics = []
        for conv in self.short_term_memory:
            # 简单的关键词提取
            user_words = conv['user'].split()
            topics.extend([w for w in user_words if len(w) > 2])
        
        # 统计词频
        topic_count = {}
        for topic in topics:
            topic_count[topic] = topic_count.get(topic, 0) + 1
        
        # 生成摘要
        top_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_topics:
            summary_topics = [topic for topic, count in top_topics]
            new_summary = f"最近讨论的主要话题: {', '.join(summary_topics)}"
            
            # 合并到长期摘要
            if self.long_term_summary:
                self.long_term_summary += f"\n{new_summary}"
            else:
                self.long_term_summary = new_summary
            
            self.save_long_term()
    
    def get_long_term_summary(self):
        """获取长期摘要"""
        return self.long_term_summary if self.long_term_summary else "暂无历史对话摘要"
    
    def save_short_term(self):
        """保存短期记忆"""
        try:
            with open(self.short_term_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.short_term_memory), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存短期记忆失败: {e}")
    
    def save_long_term(self):
        """保存长期摘要"""
        try:
            with open(self.long_term_file, 'w', encoding='utf-8') as f:
                json.dump({"summary": self.long_term_summary}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存长期摘要失败: {e}")
    
    def load_memory(self):
        """加载记忆数据"""
        # 加载短期记忆
        try:
            if os.path.exists(self.short_term_file):
                with open(self.short_term_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.short_term_memory = deque(data, maxlen=self.max_short_term)
        except Exception as e:
            print(f"加载短期记忆失败: {e}")
        
        # 加载长期摘要
        try:
            if os.path.exists(self.long_term_file):
                with open(self.long_term_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.long_term_summary = data.get("summary", "")
        except Exception as e:
            print(f"加载长期摘要失败: {e}")
    
    def clear_memory(self):
        """清空所有记忆"""
        self.short_term_memory.clear()
        self.long_term_summary = ""
        
        # 删除文件
        for file_path in [self.short_term_file, self.long_term_file]:
            if os.path.exists(file_path):
                os.remove(file_path)