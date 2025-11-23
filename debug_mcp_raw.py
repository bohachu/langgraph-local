"""
Debug script to inspect raw MCP tool definitions
檢查 MCP 原始工具定義（未經 LangChain 轉換）
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """直接連接 MCP server 檢查原始工具定義"""
    print("🔍 檢查 MCP 原始工具定義...\n")

    # 設定 MCP Server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 列出工具
            tools_result = await session.list_tools()

            print(f"📊 總共 {len(tools_result.tools)} 個工具\n")

            # 檢查前 3 個工具
            for i, tool in enumerate(tools_result.tools[:3]):
                print(f"{'='*70}")
                print(f"工具 #{i+1}: {tool.name}")
                print(f"{'='*70}")
                print(f"\n完整 MCP 工具定義:")
                print(json.dumps({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }, indent=2, ensure_ascii=False))
                print("\n")

            print(f"{'='*70}")
            print("🔍 檢查完成")
            print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
