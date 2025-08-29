# Cherry Context Plugin 使用指南

## 快速开始

### 1. 安装
```bash
pip install -r requirements_mcp.txt
```

### 2. 配置Cherry Studio
```json
{
  "mcpServers": {
    "cherry-context-v2": {
      "command": "python",
      "args": ["/path/to/cherry_context_mcp_v2.py"],
      "env": {}
    }
  }
}
```

### 3. 使用
```
@cherry-context-v2 张三的合作伙伴有哪些？
@cherry-context-v2 API接口限制是多少？
@cherry-context-v2 查找Python教程文档
```

## 功能说明

### 智能路由
- **向量检索**: 文档、教程类查询
- **SQL检索**: 配置、参数类查询  
- **图检索**: 关系、网络类查询

### 缓存机制
- 24小时自动过期
- 数据更新时自动失效
- 提升查询性能

## 数据管理

### 添加文档
```python
from cherry_plugin.plugin import CherryContextPlugin
plugin = CherryContextPlugin()
plugin.add_documents(["文档内容..."])
```

### 添加配置
```python
plugin.add_config("api_limit", "1000", "API限制")
```

### 添加关系
```python
from cherry_plugin.retriever.graph_db import GraphDB
graph_db = GraphDB()
graph_db.add_relationship("张三", "李四", "合作")
```