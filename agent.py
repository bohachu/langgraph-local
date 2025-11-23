"""
LangGraph ReAct Agent with MCP Tools - Autonomous Agentic AI
類似 Claude Code 的自主多步驟執行能力

模型建議：
- ✅ gpt-oss-20b (OpenAI) - 原生支援 function calling
- ⚠️ gemma-3n (Google) - 不支援原生 function calling，僅輸出 JSON 文字
- ✅ qwen2.5 (Alibaba) - 支援 function calling
- ✅ mistral (Mistral AI) - 支援 function calling
- ✅ llama-3.1/3.2 (Meta) - 支援 function calling
"""

import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import os


class AgenticChatBot:
    """自主執行的 Agentic AI Chatbot"""

    def __init__(self, base_url: str = "http://localhost:1234/v1", model: str = "gpt-oss-20b-mlx"):
        """
        初始化 ReAct Agent (同步版本，用於非 async 環境)

        Args:
            base_url: LM Studio API endpoint
            model: 模型名稱
        """
        self.base_url = base_url
        self.model = model
        self.llm = None
        self.tools = None
        self.agent = None
        self._initialized = False

    async def async_init(self):
        """異步初始化 (用於 async 環境如 FastAPI)"""
        if self._initialized:
            return

        print("🤖 初始化 Agentic AI...")

        # 設定 LLM (連接本地 LM Studio)
        self.llm = ChatOpenAI(
            base_url=self.base_url,
            api_key="lmstudio",  # LM Studio 不需要真實 API key
            model=self.model,
            temperature=0.7,
            streaming=True
        )

        # 設定 MCP Filesystem Server
        print("🔧 載入 MCP 工具...")

        # 載入 MCP 工具
        self.tools = await self._load_tools()

        print(f"✅ 已載入 {len(self.tools)} 個工具")

        # 建立 ReAct Agent (核心！)
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt="""你是一個自主執行的 AI 助理，類似 Claude Code。

重要行為準則：
1. 當使用者給你一個意圖或任務時，你要**自主規劃並執行所有必要步驟**
2. **不要問使用者細節**，直接根據上下文做出最佳判斷
3. 自動使用可用的工具（檔案系統、bash 等）來完成任務
4. 持續執行工具直到任務完成
5. 給出完整的最終結果，而不是中途停下來問問題

可用工具包括：
- 檔案讀取/寫入/列表
- 目錄操作

範例：
使用者: "分析當前目錄的 Python 檔案"
你應該: 自動列目錄 → 找到 .py 檔 → 讀取內容 → 分析 → 給出報告
而不是: "請問您要分析哪個檔案？"
"""
        )

        self._initialized = True
        print("🚀 Agent 已就緒！\n")

    def sync_init(self):
        """同步初始化 (用於同步環境如 CLI)"""
        asyncio.run(self.async_init())

    async def _load_tools(self):
        """非同步載入 MCP 工具"""
        connection = {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
        }

        tools = await load_mcp_tools(
            session=None,
            connection=connection,
            server_name="filesystem"
        )

        # 修正工具 schema 以符合 OpenAI/LM Studio 格式
        tools = self._fix_tool_schemas(tools)

        return tools

    def _fix_tool_schemas(self, tools):
        """
        修正 MCP 工具 schema 使其符合 OpenAI/LM Studio 格式

        問題：MCP filesystem server 的 inputSchema 只有 $schema，缺少:
        - type: "object"
        - properties: {...}
        - required: [...]

        LM Studio (OpenAI format) 要求這些欄位必須存在
        """

        # Filesystem server 工具的正確 schema 定義
        TOOL_SCHEMAS = {
            "read_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"}
                },
                "required": ["path"]
            },
            "read_text_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"},
                    "head": {"type": "integer", "description": "讀取前 N 行（可選）"},
                    "tail": {"type": "integer", "description": "讀取後 N 行（可選）"}
                },
                "required": ["path"]
            },
            "read_media_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "媒體檔案路徑"}
                },
                "required": ["path"]
            },
            "read_multiple_files": {
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "檔案路徑陣列"
                    }
                },
                "required": ["paths"]
            },
            "write_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"},
                    "content": {"type": "string", "description": "檔案內容"}
                },
                "required": ["path", "content"]
            },
            "edit_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"},
                    "edits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "oldText": {"type": "string"},
                                "newText": {"type": "string"}
                            },
                            "required": ["oldText", "newText"]
                        },
                        "description": "編輯操作陣列"
                    },
                    "dryRun": {"type": "boolean", "description": "僅預覽不執行（可選）"}
                },
                "required": ["path", "edits"]
            },
            "create_directory": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目錄路徑"}
                },
                "required": ["path"]
            },
            "list_directory": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目錄路徑"}
                },
                "required": ["path"]
            },
            "list_directory_with_sizes": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目錄路徑"},
                    "sortBy": {
                        "type": "string",
                        "enum": ["name", "size"],
                        "description": "排序方式（可選）"
                    }
                },
                "required": ["path"]
            },
            "directory_tree": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目錄路徑"},
                    "excludePatterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "排除模式（可選）"
                    }
                },
                "required": ["path"]
            },
            "move_file": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "來源路徑"},
                    "destination": {"type": "string", "description": "目標路徑"}
                },
                "required": ["source", "destination"]
            },
            "search_files": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "搜尋起始路徑"},
                    "pattern": {"type": "string", "description": "搜尋模式"},
                    "excludePatterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "排除模式（可選）"
                    }
                },
                "required": ["path", "pattern"]
            },
            "get_file_info": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案或目錄路徑"}
                },
                "required": ["path"]
            },
            "list_allowed_directories": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

        for tool in tools:
            if tool.name in TOOL_SCHEMAS:
                # 替換為正確的 schema
                tool.args_schema = TOOL_SCHEMAS[tool.name]
                print(f"✅ 已修正工具 schema: {tool.name}")

        return tools

    async def achat(self, user_message: str, thread_id: str = "default") -> str:
        """
        與 Agent 對話（異步版本，支援多輪對話和記憶）

        Agent 會自主執行多步驟來完成任務

        Args:
            user_message: 使用者訊息/意圖
            thread_id: 對話執行緒 ID（用於保持對話記憶）

        Returns:
            Agent 的最終回應
        """
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call sync_init() or async_init() first.")

        print(f"\n{'='*60}")
        print(f"👤 使用者: {user_message}")
        print(f"{'='*60}\n")
        print("🤖 Agent 思考並執行中...\n")

        # 執行 ReAct 循環（異步）
        config = {"configurable": {"thread_id": thread_id}}

        result = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        # 顯示執行過程
        print("\n--- Agent 執行軌跡 ---")
        for i, msg in enumerate(result["messages"]):
            if isinstance(msg, HumanMessage):
                print(f"  [{i}] 👤 使用者: {msg.content[:100]}...")
            elif isinstance(msg, AIMessage):
                if msg.tool_calls:
                    print(f"  [{i}] 🔧 Agent 呼叫工具: {[tc['name'] for tc in msg.tool_calls]}")
                else:
                    print(f"  [{i}] 🤖 Agent 回應: {msg.content[:100]}...")
            else:
                print(f"  [{i}] 📊 工具結果: {str(msg)[:100]}...")
        print("--- 執行完成 ---\n")

        # 取得最終回應
        final_message = result["messages"][-1].content

        print(f"\n{'='*60}")
        print(f"🤖 最終回答:\n{final_message}")
        print(f"{'='*60}\n")

        return final_message

    def chat(self, user_message: str, thread_id: str = "default") -> str:
        """
        與 Agent 對話（同步版本，支援多輪對話和記憶）

        ⚠️ 注意：此方法在異步環境中會有問題，請使用 achat() 代替

        Args:
            user_message: 使用者訊息/意圖
            thread_id: 對話執行緒 ID（用於保持對話記憶）

        Returns:
            Agent 的最終回應
        """
        return asyncio.run(self.achat(user_message, thread_id))


if __name__ == "__main__":
    # 測試範例
    agent = AgenticChatBot()
    agent.sync_init()  # 同步初始化

    # 範例 1: 自主檔案分析
    agent.chat("請列出當前目錄的所有檔案，並告訴我有哪些 Python 檔案")
