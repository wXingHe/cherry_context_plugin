# Cherry Context Plugin

智能上下文增强插件，为Cherry Studio提供多模态知识检索和上下文增强功能。

## 功能特性

- **多模态检索**: 支持向量数据库、SQL数据库、图数据库三种检索方式
- **智能路由**: 自动识别查询类型并路由到最合适的数据源
- **重排序优化**: BGE重排序提升向量检索精度，特别适合中文
- **缓存机制**: 智能缓存，数据更新时自动失效
- **MCP协议**: 完全兼容Model Context Protocol

## 前置条件

- Python 3.8+
- Cherry Studio (支持MCP协议)
- 8GB+ 内存推荐

> 详细安装指南请参考 [INSTALL.md](INSTALL.md)  
> 本地化部署请参考 [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)

## 环境准备

### 1. 克隆项目
```bash
git clone https://github.com/wXingHe/cherry_context_plugin.git
cd cherry_context_plugin
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements_mcp.txt
```

### 4. 初始化数据
```bash
python -c "from cherry_plugin.plugin import CherryContextPlugin; CherryContextPlugin()"
```

## 快速开始

### 1. 配置Cherry Studio

将以下配置添加到Cherry Studio的MCP设置中：

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

### 2. 使用插件

在Cherry Studio中使用 `@cherry-context-v2` 调用插件：

```
@cherry-context-v2 张三的合作伙伴有哪些？
@cherry-context-v2 API接口限制是多少？
@cherry-context-v2 查找Python教程文档
```

## 数据源类型

### 向量数据库 (VDB)
- **用途**: 文档检索、知识问答
- **示例**: "查找Python教程"、"搜索机器学习资料"

### SQL数据库 (SQL)  
- **用途**: 配置查询、参数设置
- **示例**: "API接口限制"、"系统配置参数"

### 图数据库 (Graph)
- **用途**: 关系查询、人员网络
- **示例**: "张三的合作伙伴"、"上下游关系"

## 项目结构

```
cherry_context_plugin/
├── cherry_plugin/           # 核心插件代码
│   ├── retriever/          # 检索模块
│   ├── routing/            # 路由模块  
│   ├── memory/             # 记忆模块
│   ├── data/               # 数据文件
│   └── ...
├── cherry_context_mcp_v2.py # MCP服务入口
├── cherry_studio_mcp_config.json # 配置示例
└── requirements_mcp.txt     # 依赖列表
```

## 配置说明

详细配置请参考：
- [Cherry Studio集成指南](CHERRY_STUDIO_INTEGRATION.md)
- [MCP配置指南](CHERRY_STUDIO_MCP_GUIDE.md)
- [使用说明](HOW_TO_USE.md)
- [重排序优化](RERANKING.md)

## 许可证

MIT License