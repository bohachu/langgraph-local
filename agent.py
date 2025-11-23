"""
LangGraph ReAct Agent with MCP Tools - Autonomous Agentic AI
類似 Claude Code 的自主多步驟執行能力
"""

from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.sessions import StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import os


class AgenticChatBot:
    """自主執行的 Agentic AI Chatbot"""

    def __init__(self, base_url: str = "http://localhost:1234/v1", model: str = "gemma-3n-e4b-it-mlx"):
        """
        初始化 ReAct Agent

        Args:
            base_url: LM Studio API endpoint
            model: 模型名稱
        """
        print("🤖 初始化 Agentic AI...")

        # 設定 LLM (連接本地 LM Studio)
        self.llm = ChatOpenAI(
            base_url=base_url,
            api_key="lmstudio",  # LM Studio 不需要真實 API key
            model=model,
            temperature=0.7,
            streaming=True
        )

        # 設定 MCP Filesystem Server
        print("🔧 載入 MCP 工具...")

        # 建立 stdio 連接到 filesystem server
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
            env=None
        )

        # 載入 MCP 工具
        with stdio_client(server_params) as (read, write):
            # 取得所有工具
            self.tools = load_mcp_tools(
                session=None,
                connection=(read, write),
                server_name="filesystem"
            )

        print(f"✅ 已載入 {len(self.tools)} 個工具")

        # 建立 ReAct Agent (核心！)
        # 這個 agent 會自主決定要執行哪些工具、執行幾次
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            # 可以自訂 system prompt 來增強 agentic 行為
            state_modifier="""你是一個自主執行的 AI 助理，類似 Claude Code。

重要行為準則：
1. 當使用者給你一個意圖或任務時，你要**自主規劃並執行所有必要步驟**
2. **不要問使用者細節**，直接根據上下文做出最佳判斷
3. 自動使用可用的工具（檔案系統、bash 等）來完成任務
4. 持續執行工具直到任務完成
5. 給出完整的最終結果，而不是中途停下來問問題

可用工具包括：
- 檔案讀取/寫入/列表
- 目錄操作
- (未來會加入 bash 執行、ripgrep 等)

範例：
使用者: "分析當前目錄的 Python 檔案"
你應該: 自動列目錄 → 找到 .py 檔 → 讀取內容 → 分析 → 給出報告
而不是: "請問您要分析哪個檔案？"
"""
        )

        print("🚀 Agent 已就緒！\n")

    def chat(self, user_message: str, thread_id: str = "default") -> str:
        """
        與 Agent 對話（支援多輪對話和記憶）

        Agent 會自主執行多步驟來完成任務

        Args:
            user_message: 使用者訊息/意圖
            thread_id: 對話執行緒 ID（用於保持對話記憶）

        Returns:
            Agent 的最終回應
        """
        print(f"\n{'='*60}")
        print(f"👤 使用者: {user_message}")
        print(f"{'='*60}\n")
        print("🤖 Agent 思考並執行中...\n")

        # 執行 ReAct 循環
        # Agent 會自動決定要執行哪些工具、執行幾次
        config = {"configurable": {"thread_id": thread_id}}

        result = self.agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        # 顯示執行過程（讓使用者看到 agentic 行為）
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


if __name__ == "__main__":
    # 測試範例
    agent = AgenticChatBot()

    # 範例 1: 自主檔案分析
    agent.chat("請列出當前目錄的所有檔案，並告訴我有哪些 Python 檔案")

    # 範例 2: 多步驟任務
    # agent.chat("建立一個叫 test.txt 的檔案，內容寫 'Hello Agentic AI'，然後讀取確認")
