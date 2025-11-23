#!/usr/bin/env python3
"""
Remote Client for LangGraph Agentic AI Server
透過 HTTP API 連接到遠端的 Agent Server
"""

import httpx
import sys
import uuid
from typing import Optional


class RemoteAgentClient:
    """遠端 Agent 客戶端"""

    def __init__(self, server_url: str = "http://localhost:8011"):
        """
        初始化遠端客戶端

        Args:
            server_url: Agent Server 的 URL
        """
        self.server_url = server_url.rstrip('/')
        self.thread_id = str(uuid.uuid4())[:8]
        self.client = httpx.Client(timeout=300.0)  # 5 分鐘 timeout

    def check_health(self) -> bool:
        """檢查伺服器健康狀態"""
        try:
            response = self.client.get(f"{self.server_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ 伺服器狀態: {data['status']}")
            print(f"🔧 可用工具數: {data['tools']}")
            return True
        except Exception as e:
            print(f"❌ 無法連接伺服器: {e}")
            return False

    def get_status(self) -> Optional[dict]:
        """取得伺服器詳細狀態"""
        try:
            response = self.client.get(f"{self.server_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 取得狀態失敗: {e}")
            return None

    def list_tools(self) -> Optional[list]:
        """列出所有可用工具"""
        try:
            response = self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            data = response.json()
            return data['tools']
        except Exception as e:
            print(f"❌ 取得工具列表失敗: {e}")
            return None

    def chat(self, message: str) -> Optional[str]:
        """
        與 Agent 對話

        Args:
            message: 使用者訊息/意圖

        Returns:
            Agent 的回應
        """
        try:
            print(f"\n{'='*60}")
            print(f"👤 你: {message}")
            print(f"{'='*60}\n")
            print("🤖 Agent 處理中...\n")

            response = self.client.post(
                f"{self.server_url}/chat",
                json={
                    "message": message,
                    "thread_id": self.thread_id,
                    "verbose": False
                }
            )
            response.raise_for_status()

            data = response.json()
            agent_response = data['response']

            print(f"\n{'='*60}")
            print(f"🤖 Agent:\n{agent_response}")
            print(f"{'='*60}\n")
            print(f"📊 對話訊息數: {data['message_count']}")

            return agent_response

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP 錯誤: {e.response.status_code}")
            print(f"   詳情: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return None

    def get_conversation_history(self) -> Optional[list]:
        """取得當前對話歷史"""
        try:
            response = self.client.get(
                f"{self.server_url}/conversations/{self.thread_id}"
            )
            response.raise_for_status()
            return response.json()['messages']
        except httpx.HTTPStatusError:
            return []
        except Exception as e:
            print(f"❌ 取得對話歷史失敗: {e}")
            return None

    def clear_conversation(self) -> bool:
        """清除當前對話歷史"""
        try:
            response = self.client.delete(
                f"{self.server_url}/conversations/{self.thread_id}"
            )
            response.raise_for_status()
            print(f"🔄 已清除對話歷史，新對話 ID: {self.thread_id}")
            self.thread_id = str(uuid.uuid4())[:8]
            return True
        except Exception as e:
            print(f"❌ 清除對話失敗: {e}")
            return False

    def close(self):
        """關閉客戶端連線"""
        self.client.close()


class InteractiveCLI:
    """互動式命令列介面"""

    def __init__(self, server_url: str = "http://localhost:8011"):
        self.client = RemoteAgentClient(server_url)

    def print_welcome(self):
        """顯示歡迎訊息"""
        print("\n" + "="*70)
        print("🤖 Remote Agentic AI Client")
        print("="*70)
        print(f"\n📡 連接伺服器: {self.client.server_url}")
        print(f"🆔 對話 ID: {self.client.thread_id}")
        print("\n可用指令:")
        print("  /help     - 顯示幫助")
        print("  /status   - 顯示伺服器狀態")
        print("  /tools    - 列出可用工具")
        print("  /history  - 顯示對話歷史")
        print("  /clear    - 清除對話記憶")
        print("  /exit     - 離開")
        print("\n特色:")
        print("  ✅ 自主多步驟執行（不需要你追問細節）")
        print("  ✅ 多輪對話記憶")
        print("  ✅ 遠端 Agent Server")
        print("  ✅ 可存取本地檔案系統（透過 MCP）")
        print("\n" + "="*70 + "\n")

    def print_help(self):
        """顯示幫助訊息"""
        print("\n📖 使用說明:")
        print("\n這是連接到遠端 LangGraph Agent Server 的客戶端。")
        print("Agent 會自主執行多步驟任務，不需要追問細節。")
        print("\n範例意圖:")
        print("  • 列出當前目錄的所有 Python 檔案")
        print("  • 分析這個專案的結構")
        print("  • 建立一個 test.txt 並寫入今天的日期")
        print()

    def show_status(self):
        """顯示伺服器狀態"""
        status = self.client.get_status()
        if status:
            print("\n📊 伺服器狀態:")
            print(f"  狀態: {status['status']}")
            print(f"  工具數: {status['tools_count']}")
            print(f"  活躍對話: {status['active_threads']}")
            print()

    def show_tools(self):
        """顯示可用工具"""
        tools = self.client.list_tools()
        if tools:
            print(f"\n🔧 可用工具 ({len(tools)} 個):")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool['name']}")
                print(f"     {tool['description']}")
            print()

    def show_history(self):
        """顯示對話歷史"""
        history = self.client.get_conversation_history()
        if history:
            print(f"\n📜 對話歷史 ({len(history)} 則):")
            for i, msg in enumerate(history, 1):
                print(f"\n  [{i}]")
                print(f"  👤 你: {msg['user'][:100]}...")
                print(f"  🤖 Agent: {msg['assistant'][:100]}...")
            print()
        else:
            print("\n📜 目前沒有對話歷史\n")

    def run(self):
        """執行主迴圈"""
        self.print_welcome()

        # 檢查伺服器連線
        if not self.client.check_health():
            print("\n請確認:")
            print("  1. Server 已啟動 (./sh/server.sh)")
            print("  2. Server 位址正確")
            return

        print()

        # 主對話迴圈
        while True:
            try:
                user_input = input("💬 你: ").strip()

                if not user_input:
                    continue

                # 處理指令
                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command in ["/exit", "/quit"]:
                        print("\n👋 再見！\n")
                        break

                    elif command == "/help":
                        self.print_help()

                    elif command == "/status":
                        self.show_status()

                    elif command == "/tools":
                        self.show_tools()

                    elif command == "/history":
                        self.show_history()

                    elif command == "/clear":
                        self.client.clear_conversation()

                    else:
                        print(f"\n❓ 未知指令: {user_input}")
                        print("輸入 /help 查看可用指令\n")

                    continue

                # 一般對話
                self.client.chat(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 收到中斷信號，再見！\n")
                break

            except EOFError:
                print("\n\n👋 再見！\n")
                break

        # 清理
        self.client.close()


if __name__ == "__main__":
    # 從命令列參數取得 server URL
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    cli = InteractiveCLI(server_url)
    cli.run()
