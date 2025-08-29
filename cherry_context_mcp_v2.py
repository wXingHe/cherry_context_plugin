#!/usr/bin/env python3
"""
Cherry Context MCP Server V2 - 强制重新加载
"""
import asyncio
import sys
import json
import importlib
import os

sys.path.append('/home/feliexw/Documents/Demo/AI/cherry_context_plugin')

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

server = Server("cherry-context-v2")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="enhance_prompt",
            description="增强用户问题的上下文，通过检索相关信息生成更完整的prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户的原始问题"
                    }
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name != "enhance_prompt":
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments or "question" not in arguments:
        raise ValueError("Missing required argument: question")
    
    question = arguments["question"]
    
    try:
        # 强制重新导入模块
        modules_to_reload = [
            'cherry_plugin.plugin',
            'cherry_plugin.retriever.graph_db', 
            'cherry_plugin.retriever.sql_db',
            'cherry_plugin.retriever.vector_db'
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                importlib.reload(sys.modules[module])
            
        from cherry_plugin.plugin import CherryContextPlugin
        
        # 每次都创建新实例
        plugin = CherryContextPlugin()
        result = plugin.process_question(question)
        
        enhanced_prompt = result["final_prompt"]
        info = f"路由: {result['route']} | 检索: {len(result['retrieved'])}条"
        
        # 如果是图检索，显示具体结果
        debug_info = ""
        if result['route'] == 'graph' and result['retrieved']:
            debug_info = f"\n检索详情: {result['retrieved']}"
        
        return [
            types.TextContent(
                type="text",
                text=f"{enhanced_prompt}\n\n<!-- MCP处理信息: {info}{debug_info} -->"
            )
        ]
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return [
            types.TextContent(
                type="text", 
                text=f"处理失败: {str(e)}\n\n错误详情:\n{error_detail}\n\n原始问题: {question}"
            )
        ]

async def main():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cherry-context-v2",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())