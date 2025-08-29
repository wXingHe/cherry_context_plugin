@echo off
REM Cherry Context Plugin Windows 本地化部署脚本

echo 🍒 Cherry Context Plugin 本地化部署
echo ==================================

REM 检查Python
echo 📋 检查Python环境...
python --version >nul 2>&1 || (
    echo ❌ 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION%

REM 创建虚拟环境
echo 🔧 创建虚拟环境...
python -m venv cherry_env
call cherry_env\Scripts\activate

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装依赖包...
pip install -r requirements_mcp.txt

REM 提示安装LM Studio
echo 🤖 本地LLM设置...
echo 请手动完成以下步骤:
echo   1. 下载LM Studio: https://lmstudio.ai/
echo   2. 安装并启动LM Studio
echo   3. 下载中文模型: Qwen2.5-1.5B-Instruct-GGUF
echo   4. 启动本地服务器 (端口1234)
echo.
pause

REM 初始化插件
echo 🔧 初始化插件...
python -c "try: from cherry_plugin.plugin import CherryContextPlugin; plugin = CherryContextPlugin(); print('✅ 插件初始化成功'); except Exception as e: print(f'❌ 插件初始化失败: {e}'); exit(1)"

REM 性能测试
echo 🧪 运行性能测试...
python -c "import time; from cherry_plugin.plugin import CherryContextPlugin; plugin = CherryContextPlugin(); test_queries = ['张三的合作伙伴有哪些？', 'API接口限制是多少？', '查找Python教程文档']; print('性能测试结果:'); [print(f'  {query}: {(lambda: (time.time(), plugin.process_question(query), time.time()))()[1][\"route\"]} | {len((lambda: (time.time(), plugin.process_question(query), time.time()))()[1][\"retrieved\"])}条') for query in test_queries]"

echo ==================================
echo 🎉 部署完成！
echo.
echo 📋 服务信息:
echo   LM Studio: http://localhost:1234
echo   插件路径: %CD%\cherry_context_mcp_v2.py
echo.
echo 📝 下一步:
echo   1. 确保LM Studio服务运行
echo   2. 配置Cherry Studio MCP设置
echo   3. 参考README.md开始使用
echo.
pause