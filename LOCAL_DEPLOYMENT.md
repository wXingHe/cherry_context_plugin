# 本地化部署指南

## 硬件要求

### 推荐配置
- **CPU**: 8核以上
- **内存**: 16GB+
- **存储**: 10GB+ 可用空间
- **GPU**: 可选，8GB+ 显存用于LLM加速

### 最低配置
- **CPU**: 4核
- **内存**: 8GB
- **存储**: 5GB+ 可用空间

## 本地LLM部署

### 方案1: Ollama (推荐)

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载中文模型
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:7b  # 可选，更好效果但需更多内存

# 启动服务
ollama serve
```

### 方案2: LM Studio

1. 下载 [LM Studio](https://lmstudio.ai/)
2. 搜索并下载中文模型：
   - `Qwen2.5-1.5B-Instruct-GGUF`
   - `BGE-small-zh` (Embedding模型)
3. 启动本地服务器 (默认端口1234)

## 向量模型部署

### 中文Embedding模型

```python
# 自动下载中文优化模型
from sentence_transformers import SentenceTransformer

# 方案1: 通用中文模型
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 方案2: 专门中文模型 (推荐)
model = SentenceTransformer('shibing624/text2vec-base-chinese')

# 方案3: BGE中文模型 (最佳效果)
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
```

### 离线模型部署

```bash
# 预下载模型到本地
mkdir -p models/
cd models/

# 下载中文Embedding模型
git clone https://huggingface.co/BAAI/bge-small-zh-v1.5

# 在代码中使用本地路径
model = SentenceTransformer('./models/bge-small-zh-v1.5')
```

## 数据库配置

### SQLite (默认)
- 无需额外安装
- 适合中小型数据
- 文件存储，便于备份

### PostgreSQL (可选)
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb cherry_context

# 配置连接
export DATABASE_URL="postgresql://user:password@localhost/cherry_context"
```

### Neo4j (图数据库，可选)
```bash
# 下载Neo4j Community Edition
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# 启动服务
sudo systemctl start neo4j
# 访问 http://localhost:7474
```

## 完整部署脚本

### 一键部署脚本

```bash
#!/bin/bash
# deploy_local.sh

echo "🍒 Cherry Context Plugin 本地化部署"

# 1. 检查Python环境
python3 --version || { echo "请先安装Python 3.8+"; exit 1; }

# 2. 创建虚拟环境
python3 -m venv cherry_env
source cherry_env/bin/activate

# 3. 安装依赖
pip install -r requirements_mcp.txt

# 4. 安装Ollama
if ! command -v ollama &> /dev/null; then
    echo "安装Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# 5. 下载模型
echo "下载中文LLM模型..."
ollama pull qwen2.5:1.5b

# 6. 启动Ollama服务
ollama serve &
sleep 5

# 7. 初始化插件
python -c "from cherry_plugin.plugin import CherryContextPlugin; CherryContextPlugin()"

echo "✅ 部署完成！"
echo "Ollama服务: http://localhost:11434"
echo "请配置Cherry Studio MCP设置"
```

### Windows部署脚本

```batch
@echo off
REM deploy_local.bat

echo 🍒 Cherry Context Plugin 本地化部署

REM 1. 检查Python
python --version >nul 2>&1 || (
    echo 请先安装Python 3.8+
    exit /b 1
)

REM 2. 创建虚拟环境
python -m venv cherry_env
call cherry_env\Scripts\activate

REM 3. 安装依赖
pip install -r requirements_mcp.txt

REM 4. 下载LM Studio (手动)
echo 请手动下载并安装LM Studio: https://lmstudio.ai/

REM 5. 初始化插件
python -c "from cherry_plugin.plugin import CherryContextPlugin; CherryContextPlugin()"

echo ✅ 部署完成！
pause
```

## 配置优化

### 内存优化配置

```python
# cherry_plugin/config.json
{
  "settings": {
    "vector_search_k": 3,        # 减少检索数量
    "cache_expire_hours": 48,    # 延长缓存时间
    "prompt_max_length": 2000,   # 限制prompt长度
    "batch_size": 16             # 批处理大小
  },
  "models": {
    "embedding_model": "BAAI/bge-small-zh-v1.5",
    "llm_endpoint": "http://localhost:11434",
    "llm_model": "qwen2.5:1.5b"
  }
}
```

### 路由优化

```python
# 针对中文优化的路由示例
module_examples = {
    "vdb": [
        "查找文档内容", "搜索资料", "历史对话", 
        "笔记检索", "知识查询", "文献搜索"
    ],
    "sql": [
        "配置参数", "系统设置", "API限制", 
        "数据库查询", "规则配置", "参数设置"
    ],
    "graph": [
        "人员关系", "组织架构", "合作伙伴", 
        "上下游关系", "知识图谱", "关系网络"
    ]
}
```

## 性能监控

### 资源监控脚本

```python
# monitor.py
import psutil
import time

def monitor_resources():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        print(f"CPU: {cpu}% | 内存: {memory}%")
        time.sleep(5)

if __name__ == "__main__":
    monitor_resources()
```

### 性能测试

```python
# benchmark.py
import time
from cherry_plugin.plugin import CherryContextPlugin

def benchmark():
    plugin = CherryContextPlugin()
    
    test_queries = [
        "张三的合作伙伴有哪些？",
        "API接口限制是多少？", 
        "查找Python教程文档"
    ]
    
    for query in test_queries:
        start = time.time()
        result = plugin.process_question(query)
        end = time.time()
        
        print(f"查询: {query}")
        print(f"路由: {result['route']}")
        print(f"耗时: {end-start:.2f}秒")
        print(f"结果: {len(result['retrieved'])}条")
        print("-" * 50)

if __name__ == "__main__":
    benchmark()
```

## 故障排除

### 常见问题

1. **Ollama连接失败**
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 重启服务
pkill ollama
ollama serve
```

2. **内存不足**
```python
# 使用更小的模型
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# 减少批处理大小
batch_size = 8
```

3. **中文识别问题**
```python
# 使用专门的中文模型
model = SentenceTransformer('shibing624/text2vec-base-chinese')
```

## 生产环境部署

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements_mcp.txt

# 下载模型
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"

EXPOSE 8000
CMD ["python", "cherry_context_mcp_v2.py"]
```

```bash
# 构建和运行
docker build -t cherry-context .
docker run -p 8000:8000 -v ./data:/app/cherry_plugin/data cherry-context
```

### 服务化部署

```bash
# systemd服务文件
sudo tee /etc/systemd/system/cherry-context.service << EOF
[Unit]
Description=Cherry Context Plugin
After=network.target

[Service]
Type=simple
User=cherry
WorkingDirectory=/opt/cherry_context_plugin
ExecStart=/opt/cherry_context_plugin/venv/bin/python cherry_context_mcp_v2.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable cherry-context
sudo systemctl start cherry-context
```