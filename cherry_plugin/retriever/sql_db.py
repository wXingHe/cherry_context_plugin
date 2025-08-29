"""
SQL检索模块：SQLite结构化数据检索
"""
import sqlite3
import os
import re

class SqlDB:
    def __init__(self, db_path="cherry_plugin/data/config.db"):
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                category TEXT
            )
        ''')
        
        # 创建规则表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                condition TEXT,
                action TEXT,
                category TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {self.db_path}")
    
    def add_config(self, key, value, description="", category="general"):
        """添加配置项"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, description, category)
            VALUES (?, ?, ?, ?)
        ''', (key, value, description, category))
        
        conn.commit()
        conn.close()
    
    def add_rule(self, name, condition, action, category="general"):
        """添加规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rules (name, condition, action, category)
            VALUES (?, ?, ?, ?)
        ''', (name, condition, action, category))
        
        conn.commit()
        conn.close()
    
    def extract_keywords(self, question):
        """从问题中提取关键词"""
        keywords = []
        
        # 直接匹配常见关键词
        if 'API' in question or 'api' in question.lower():
            keywords.extend(['api', 'API'])
        if '限制' in question:
            keywords.extend(['限制', 'limit'])
        if '接口' in question:
            keywords.extend(['接口', 'interface'])
        if '配置' in question:
            keywords.extend(['配置', 'config'])
        if '参数' in question:
            keywords.extend(['参数', 'param'])
            
        # 提取英文单词
        english_words = re.findall(r'[A-Za-z]+', question)
        keywords.extend([w.lower() for w in english_words if len(w) > 2])
        
        # 提取中文词汇
        chinese_words = re.findall(r'[一-鿿]+', question)
        keywords.extend([w for w in chinese_words if len(w) >= 2])
        
        return list(set(keywords))
    
    def search_config(self, question, limit=5):
        """搜索配置项"""
        keywords = self.extract_keywords(question)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        
        # 精确匹配
        for keyword in keywords:
            cursor.execute('''
                SELECT key, value, description, category FROM config 
                WHERE key LIKE ? OR description LIKE ?
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit))
            
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    'type': 'config',
                    'key': row[0],
                    'value': row[1],
                    'description': row[2],
                    'category': row[3],
                    'match_keyword': keyword
                })
        
        conn.close()
        return results[:limit]
    
    def search_rules(self, question, limit=5):
        """搜索规则"""
        keywords = self.extract_keywords(question)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        
        for keyword in keywords:
            cursor.execute('''
                SELECT id, name, condition, action, category FROM rules 
                WHERE name LIKE ? OR condition LIKE ? OR action LIKE ?
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    'type': 'rule',
                    'id': row[0],
                    'name': row[1],
                    'condition': row[2],
                    'action': row[3],
                    'category': row[4],
                    'match_keyword': keyword
                })
        
        conn.close()
        return results[:limit]
    
    def search(self, question, limit=5):
        """综合搜索"""
        config_results = self.search_config(question, limit//2 + 1)
        rule_results = self.search_rules(question, limit//2 + 1)
        
        all_results = config_results + rule_results
        return all_results[:limit]