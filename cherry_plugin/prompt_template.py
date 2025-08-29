"""
提示模板模块：动态prompt生成和优化
"""

class PromptTemplate:
    def __init__(self):
        self.templates = {
            "default": """系统指令: 你是智能中文助手。

{context_sections}

用户问题:
{user_question}""",
            
            "with_memory": """系统指令: 你是智能中文助手，请结合对话历史回答问题。

{context_sections}

用户问题:
{user_question}""",
            
            "technical": """系统指令: 你是技术专家助手，请提供准确的技术信息。

{context_sections}

用户问题:
{user_question}

请提供详细的技术解答。"""
        }
    
    def build_context_sections(self, short_term=None, retrieved=None, long_term=None):
        """构建上下文部分"""
        sections = []
        
        if short_term:
            sections.append(f"短期对话记忆:\n{short_term}")
        
        if retrieved:
            if isinstance(retrieved, list):
                retrieved_text = "\n".join([str(item) for item in retrieved])
            else:
                retrieved_text = str(retrieved)
            sections.append(f"相关知识检索结果:\n{retrieved_text}")
        
        if long_term and long_term != "暂无历史对话摘要":
            sections.append(f"长期摘要:\n{long_term}")
        
        return "\n\n".join(sections)
    
    def generate_prompt(self, user_question, short_term=None, retrieved=None, 
                       long_term=None, template_type="default"):
        """生成最终prompt"""
        context_sections = self.build_context_sections(short_term, retrieved, long_term)
        
        template = self.templates.get(template_type, self.templates["default"])
        
        return template.format(
            context_sections=context_sections,
            user_question=user_question
        )
    
    def optimize_prompt_length(self, prompt, max_length=4000):
        """优化prompt长度"""
        if len(prompt) <= max_length:
            return prompt
        
        # 简单的截断策略：保留系统指令和用户问题，压缩中间内容
        lines = prompt.split('\n')
        system_lines = []
        user_question_lines = []
        context_lines = []
        
        in_user_question = False
        for line in lines:
            if line.startswith("用户问题:"):
                in_user_question = True
            
            if in_user_question:
                user_question_lines.append(line)
            elif line.startswith("系统指令:"):
                system_lines.append(line)
            else:
                context_lines.append(line)
        
        # 保留系统指令和用户问题，压缩上下文
        essential_text = '\n'.join(system_lines + user_question_lines)
        remaining_length = max_length - len(essential_text) - 100  # 留一些缓冲
        
        if remaining_length > 0:
            context_text = '\n'.join(context_lines)
            if len(context_text) > remaining_length:
                context_text = context_text[:remaining_length] + "...(内容已截断)"
            
            return '\n'.join(system_lines + [context_text] + user_question_lines)
        else:
            return essential_text