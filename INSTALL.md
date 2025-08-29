# 安装指南

## 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 建议 8GB 以上
- **存储**: 至少 1GB 可用空间

## 依赖检查

### 检查Python版本
```bash
python --version
# 或
python3 --version
```

### 检查pip
```bash
pip --version
# 或
pip3 --version
```

## 安装步骤

### 1. 下载项目
```bash
# 方式1: Git克隆
git clone https://github.com/wXingHe/cherry_context_plugin.git
cd cherry_context_plugin

# 方式2: 下载ZIP
# 从GitHub下载ZIP文件并解压
```

### 2. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv cherry_env

# 激活虚拟环境
# Linux/Mac:
source cherry_env/bin/activate
# Windows:
cherry_env\Scripts\activate
```

### 3. 安装依赖
```bash
# 安装MCP依赖
pip install -r requirements_mcp.txt

# 验证安装
python -c "import sentence_transformers; print('安装成功')"
```

### 4. 初始化数据
```bash
# 创建必要的数据文件
python -c "
from cherry_plugin.plugin import CherryContextPlugin
plugin = CherryContextPlugin()
print('初始化完成')
"
```

## 验证安装

### 测试插件功能
```bash
python -c "
from cherry_plugin.plugin import CherryContextPlugin
plugin = CherryContextPlugin()
result = plugin.process_question('测试查询')
print(f'测试成功: {result[\"route\"]}')
"
```

### 测试MCP服务
```bash
# 启动MCP服务（测试模式）
timeout 5s python cherry_context_mcp_v2.py << EOF
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}
EOF
```

## 常见问题

### 1. Python版本过低
```bash
# 升级Python或使用pyenv
pyenv install 3.9.0
pyenv local 3.9.0
```

### 2. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements_mcp.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 权限问题
```bash
# 使用用户安装
pip install --user -r requirements_mcp.txt
```

### 4. 内存不足
- 关闭其他应用程序
- 使用较小的向量模型
- 调整缓存设置

## 卸载

```bash
# 删除虚拟环境
rm -rf cherry_env

# 删除项目文件
rm -rf cherry_context_plugin
```