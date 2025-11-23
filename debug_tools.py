"""
Debug script to inspect MCP tool schemas
檢查 MCP 工具的實際 schema 格式
"""

import asyncio
import json
from agent import AgenticChatBot


async def main():
    """檢查工具的 schema 格式"""
    print("🔍 檢查 MCP 工具 Schema 格式...\n")

    agent = AgenticChatBot()
    await agent.async_init()

    print(f"\n📊 總共 {len(agent.tools)} 個工具\n")

    # 只檢查前 3 個工具作為範例
    for i, tool in enumerate(agent.tools[:3]):
        print(f"{'='*70}")
        print(f"工具 #{i+1}: {tool.name}")
        print(f"{'='*70}")
        print(f"描述: {tool.description[:100]}...")

        # 檢查 args_schema
        if hasattr(tool, 'args_schema'):
            print(f"\n✅ 有 args_schema (type: {type(tool.args_schema).__name__})")
            try:
                schema = tool.args_schema.schema()
                print(f"\nargs_schema.schema() 結構:")
                print(json.dumps(schema, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"❌ 無法取得 schema: {e}")
        else:
            print(f"\n❌ 沒有 args_schema")

        # 檢查 LangChain tool 轉換成 OpenAI format
        try:
            from langchain_core.utils.function_calling import convert_to_openai_tool
            openai_format = convert_to_openai_tool(tool)
            print(f"\n🔧 OpenAI 格式 (convert_to_openai_tool):")
            print(json.dumps(openai_format, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ 無法轉換成 OpenAI 格式: {e}")

        print("\n")

    print(f"\n{'='*70}")
    print("🔍 檢查完成")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
