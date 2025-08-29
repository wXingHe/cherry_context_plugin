#!/bin/bash
# Cherry Context Plugin 本地化部署脚本

set -e

echo "🍒 Cherry Context Plugin 本地化部署"
echo "=================================="

# 检查Python版本
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION"

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
python3 -m venv cherry_env
source cherry_env/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements_mcp.txt

# 检查Ollama
echo "🤖 检查Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "📥 安装Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama已安装"
fi

# 启动Ollama服务
echo "🚀 启动Ollama服务..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# 下载中文模型
echo "📥 下载中文LLM模型..."
ollama pull qwen2.5:1.5b

# 初始化插件
echo "🔧 初始化插件..."
python -c "
try:
    from cherry_plugin.plugin import CherryContextPlugin
    plugin = CherryContextPlugin()
    print('✅ 插件初始化成功')
except Exception as e:
    print(f'❌ 插件初始化失败: {e}')
    exit(1)
"

# 性能测试
echo "🧪 运行性能测试..."
python -c "
import time
from cherry_plugin.plugin import CherryContextPlugin

plugin = CherryContextPlugin()
test_queries = [
    '张三的合作伙伴有哪些？',
    'API接口限制是多少？', 
    '查找Python教程文档'
]

print('性能测试结果:')
for query in test_queries:
    start = time.time()
    result = plugin.process_question(query)
    end = time.time()
    print(f'  {query}: {result[\"route\"]} | {len(result[\"retrieved\"])}条 | {end-start:.2f}秒')
"

echo "=================================="
echo "🎉 部署完成！"
echo ""
echo "📋 服务信息:"
echo "  Ollama服务: http://localhost:11434"
echo "  插件路径: $(pwd)/cherry_context_mcp_v2.py"
echo ""
echo "📝 下一步:"
echo "  1. 配置Cherry Studio MCP设置"
echo "  2. 参考README.md开始使用"
echo ""
echo "🔧 管理命令:"
echo "  启动虚拟环境: source cherry_env/bin/activate"
echo "  停止Ollama: kill $OLLAMA_PID"