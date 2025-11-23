"""
簡化版 Agent - 不使用 MCP 工具，用於測試基本對話功能
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage


class SimpleAgenticChatBot:
    """簡化版 Agentic AI Chatbot（無工具）"""

    def __init__(self, base_url: str = "http://localhost:1234/v1", model: str = "gemma-3n-e4b-it-mlx"):
        self.base_url = base_url
        self.model = model
        self.llm = None
        self.agent = None
        self._initialized = False

    async def async_init(self):
        """異步初始化"""
        if self._initialized:
            return

        print("🤖 初始化簡化版 Agentic AI（無工具）...")

        # 設定 LLM
        self.llm = ChatOpenAI(
            base_url=self.base_url,
            api_key="lmstudio",
            model=self.model,
            temperature=0.7,
            streaming=False
        )

        # 建立不使用工具的 Agent
        self.agent = create_react_agent(
            self.llm,
            tools=[],  # 空工具列表
            prompt="你是一個友善的 AI 助理。請用繁體中文回答使用者的問題。"
        )

        self._initialized = True
        print("🚀 簡化版 Agent 已就緒！\n")

    def sync_init(self):
        """同步初始化"""
        import asyncio
        asyncio.run(self.async_init())

    def chat(self, user_message: str, thread_id: str = "default") -> str:
        """與 Agent 對話"""
        if not self._initialized:
            raise RuntimeError("Agent not initialized")

        config = {"configurable": {"thread_id": thread_id}}

        result = self.agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        return result["messages"][-1].content


if __name__ == "__main__":
    agent = SimpleAgenticChatBot()
    agent.sync_init()
    response = agent.chat("你好")
    print(f"Agent: {response}")
