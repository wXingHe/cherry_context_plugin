"""
缓存模块：提升检索性能
"""
import json
import os
import hashlib
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir="cherry_plugin/data/cache", expire_hours=24):
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(cache_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(base_dir, cache_dir)
        self.cache_dir = cache_dir
        self.expire_hours = expire_hours
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, query, route_type):
        """生成缓存键"""
        content = f"{query}_{route_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query, route_type):
        """获取缓存结果"""
        cache_key = self._get_cache_key(query, route_type)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查时间过期
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.expire_hours):
                os.remove(cache_path)
                return None
            
            # 检查数据文件是否更新
            if self._is_data_updated(route_type, cached_time):
                os.remove(cache_path)
                return None
            
            return cache_data['result']
        
        except Exception as e:
            print(f"读取缓存失败: {e}")
            return None
    
    def _is_data_updated(self, route_type, cached_time):
        """检查数据文件是否在缓存后更新"""
        data_files = {
            'graph': 'cherry_plugin/data/graph_data.json',
            'sql': 'cherry_plugin/data/config.db', 
            'vdb': 'cherry_plugin/data/vector_db.index'
        }
        
        data_file = data_files.get(route_type)
        if not data_file or not os.path.exists(data_file):
            return False
            
        file_mtime = datetime.fromtimestamp(os.path.getmtime(data_file))
        return file_mtime > cached_time
    
    def set(self, query, route_type, result):
        """设置缓存"""
        cache_key = self._get_cache_key(query, route_type)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'route_type': route_type,
            'result': result
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存失败: {e}")
    
    def clear_expired(self):
        """清理过期缓存"""
        if not os.path.exists(self.cache_dir):
            return
        
        expired_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > timedelta(hours=self.expire_hours):
                        os.remove(filepath)
                        expired_count += 1
                
                except Exception:
                    # 删除损坏的缓存文件
                    os.remove(filepath)
                    expired_count += 1
        
        print(f"清理了 {expired_count} 个过期缓存文件")