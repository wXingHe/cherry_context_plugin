# Cherry Studio MCP集成指南

## 🎯 方案2实现：MCP返回增强Prompt

### 1. 安装依赖
```bash
cd cherry_context_plugin
pip install mcp
```

### 2. 测试MCP服务器
```bash
python test_mcp.py
```

### 3. 在Cherry Studio中配置MCP

#### 方法1：通过界面配置
1. 打开Cherry Studio
2. 进入 **设置** → **MCP服务器**
3. 点击 **添加服务器**
4. 填写配置：
   - **名称**: `cherry-context`
   - **命令**: `python`
   - **参数**: `/home/feliexw/Documents/Demo/AI/cherry_context_plugin/cherry_context_mcp.py`
   - **类型**: `stdio`

#### 方法2：配置文件
复制配置到Cherry Studio的MCP配置文件：
```json
{
  "mcpServers": {
    "cherry-context": {
      "command": "python",
      "args": ["/home/feliexw/Documents/Demo/AI/cherry_context_plugin/cherry_context_mcp.py"],
      "env": {}
    }
  }
}
```

### 4. 使用方法

#### 在对话中调用工具
1. 在Cherry Studio中开始对话
2. 输入问题，如："Python有什么特点？"
3. Cherry Studio会自动检测到MCP工具
4. 选择使用 `enhance_prompt` 工具
5. 工具会返回增强后的prompt
6. Cherry Studio使用增强后的prompt生成回答

#### 示例对话流程
```
用户: "Python编程语言有什么特点？"
↓
Cherry Studio检测到MCP工具
↓
调用enhance_prompt工具
↓
返回增强后的prompt（包含相关文档、配置、记忆）
↓
Cherry Studio使用增强prompt生成最终回答
```

### 5. 工具说明

**enhance_prompt工具**：
- **输入**: 用户的原始问题
- **输出**: 增强后的完整prompt
- **功能**: 
  - 智能路由（vdb/sql/graph）
  - 检索相关信息
  - 整合对话记忆
  - 生成结构化prompt

### 6. 优势

✅ **保持Cherry Studio体验**：用户界面和操作习惯不变
✅ **智能上下文增强**：自动检索和整合相关信息  
✅ **灵活调用**：用户可选择是否使用增强功能
✅ **完整集成**：利用Cherry Studio的模型管理和对话功能

### 7. 故障排除

**MCP服务器无法启动**：
- 检查Python路径是否正确
- 确认依赖包已安装：`pip list | grep mcp`
- 查看Cherry Studio日志

**工具调用失败**：
- 确认Ollama服务运行：`ollama list`
- 检查数据文件是否存在：`ls cherry_plugin/data/`
- 运行测试脚本：`python test_mcp.py`

**检索结果为空**：
- 重新初始化数据：`python init_data.py`
- 检查向量数据库：确认文档已加载

### 8. 自定义配置

可以修改 `cherry_context_mcp.py` 中的参数：
- 检索数量
- 路由阈值  
- 缓存设置
- 模板格式

现在你可以在Cherry Studio中通过MCP使用上下文增强功能了！