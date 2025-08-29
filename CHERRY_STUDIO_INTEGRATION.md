# Cherry Studio 插件集成指南

## 1. 准备插件包

### 创建插件包结构
```
cherry_context_plugin/
├── manifest.json          # 插件清单文件
├── main.py                # 插件入口文件
├── cherry_plugin/         # 核心模块
└── requirements.txt       # 依赖文件
```

### 检查依赖环境
- ✅ Python 3.10+ 虚拟环境
- ✅ Ollama服务运行中 (localhost:11434)
- ✅ 所有Python包已安装

## 2. Cherry Studio插件目录

### 查找插件目录
```bash
# Linux/Mac
~/.cherry-studio/plugins/

# Windows  
%APPDATA%/cherry-studio/plugins/

# 或在Cherry Studio设置中查看插件路径
```

### 复制插件文件
```bash
# 复制整个插件目录到Cherry Studio插件目录
cp -r cherry_context_plugin ~/.cherry-studio/plugins/
```

## 3. 在Cherry Studio中启用插件

### 步骤：
1. 打开Cherry Studio
2. 进入 设置 → 插件管理
3. 找到 "Cherry Context Plugin"
4. 点击 "启用" 按钮
5. 配置插件参数（可选）

### 插件配置参数：
- `max_short_term_memory`: 短期记忆轮数 (默认: 10)
- `cache_expire_hours`: 缓存过期时间 (默认: 24)
- `vector_search_k`: 向量检索数量 (默认: 5)
- `route_threshold`: 路由阈值 (默认: 0.1)

## 4. 测试插件功能

### 基础功能测试
1. **向量检索测试**
   - 问题: "Python编程语言的特点"
   - 预期: 从文档库检索相关内容

2. **SQL检索测试**  
   - 问题: "系统配置参数有哪些"
   - 预期: 从配置表检索结构化数据

3. **图检索测试**
   - 问题: "张三的合作伙伴"
   - 预期: 从关系图检索人员关系

4. **记忆功能测试**
   - 进行多轮对话
   - 预期: 后续回答包含前面的对话上下文

### 性能测试
- 响应时间 < 3秒
- 缓存命中率 > 50%
- 路由准确率 > 80%

## 5. 故障排除

### 常见问题：
1. **插件无法加载**
   - 检查Python环境路径
   - 确认依赖包完整安装
   - 查看Cherry Studio日志

2. **Ollama连接失败**
   - 确认Ollama服务运行: `ollama list`
   - 检查端口11434是否可访问
   - 重启Ollama服务

3. **检索结果为空**
   - 检查数据文件是否存在
   - 运行数据初始化脚本
   - 查看插件日志输出

### 日志查看：
```bash
# Cherry Studio日志位置
~/.cherry-studio/logs/
```

## 6. 数据管理

### 初始化数据
```bash
# 运行数据初始化脚本
python init_data.py
```

### 备份数据
```bash
# 备份插件数据
cp -r cherry_plugin/data/ backup/
```

### 清理缓存
```bash
# 清理过期缓存
python -c "from cherry_plugin.cache import CacheManager; CacheManager().clear_expired()"
```