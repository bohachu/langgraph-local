#!/usr/bin/env python3
"""
Terminal Chat Client for Agentic AI
支援多輪對話、對話記憶、指令控制
"""

import sys
import uuid
from agent import AgenticChatBot


class TerminalChatClient:
    """互動式 Terminal 客戶端"""

    def __init__(self):
        self.agent = None
        self.thread_id = str(uuid.uuid4())[:8]  # 每次啟動新的對話執行緒

    def print_welcome(self):
        """顯示歡迎訊息"""
        print("\n" + "="*70)
        print("🤖 Agentic AI Chat - 類似 Claude Code 的自主執行 AI")
        print("="*70)
        print("\n可用指令:")
        print("  /help     - 顯示幫助")
        print("  /clear    - 清除對話記憶（開始新對話）")
        print("  /info     - 顯示當前狀態")
        print("  /exit     - 離開")
        print("\n特色:")
        print("  ✅ 自主多步驟執行（不需要你追問細節）")
        print("  ✅ 多輪對話記憶")
        print("  ✅ 可存取本地檔案系統")
        print("  ✅ 使用本地 LM Studio (gemma-3n-e4b-it-mlx)")
        print("\n範例意圖:")
        print("  • 列出當前目錄的所有 Python 檔案並統計行數")
        print("  • 建立一個 hello.txt 檔案，內容是今天的日期")
        print("  • 分析這個專案的結構並給我建議")
        print("\n" + "="*70 + "\n")

    def print_help(self):
        """顯示幫助訊息"""
        print("\n📖 使用說明:")
        print("\n這是一個 **自主執行的 AI Agent**，類似 Claude Code。")
        print("\n與傳統 chatbot 的差異:")
        print("  ❌ 傳統: '請問你要分析哪個檔案？' (需要追問)")
        print("  ✅ Agentic: 自動列目錄 → 找檔案 → 分析 → 給結果")
        print("\n它會:")
        print("  1. 理解你的意圖")
        print("  2. 自主規劃步驟")
        print("  3. 自動呼叫工具（檔案操作等）")
        print("  4. 循環執行直到完成")
        print("  5. 給你完整結果")
        print("\n你只需要:")
        print("  • 告訴它你想做什麼（意圖）")
        print("  • 不用提供所有細節，它會自己判斷")
        print()

    def print_info(self):
        """顯示當前狀態"""
        print(f"\n📊 當前狀態:")
        print(f"  對話 ID: {self.thread_id}")
        print(f"  LM Studio: http://localhost:1234/v1")
        print(f"  模型: gemma-3n-e4b-it-mlx")
        if self.agent:
            print(f"  可用工具數: {len(self.agent.tools)}")
        print()

    def clear_conversation(self):
        """清除對話記憶"""
        self.thread_id = str(uuid.uuid4())[:8]
        print(f"\n🔄 已清除對話記憶，新對話 ID: {self.thread_id}\n")

    def run(self):
        """執行主迴圈"""
        self.print_welcome()

        # 初始化 Agent
        try:
            print("正在連接 LM Studio 並初始化 Agent...\n")
            self.agent = AgenticChatBot()
        except Exception as e:
            print(f"\n❌ 初始化失敗: {e}")
            print("\n請確認:")
            print("  1. LM Studio 已啟動並載入模型")
            print("  2. API Server 正在運行於 http://localhost:1234")
            print("  3. 已安裝所有相依套件 (pip install -r requirements.txt)")
            return

        # 主對話迴圈
        while True:
            try:
                # 讀取使用者輸入
                user_input = input("\n💬 你: ").strip()

                if not user_input:
                    continue

                # 處理指令
                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command == "/exit" or command == "/quit":
                        print("\n👋 再見！\n")
                        break

                    elif command == "/help":
                        self.print_help()

                    elif command == "/info":
                        self.print_info()

                    elif command == "/clear":
                        self.clear_conversation()

                    else:
                        print(f"\n❓ 未知指令: {user_input}")
                        print("輸入 /help 查看可用指令\n")

                    continue

                # 一般對話 - 讓 Agent 自主執行
                try:
                    self.agent.chat(user_input, thread_id=self.thread_id)
                except Exception as e:
                    print(f"\n❌ Agent 執行錯誤: {e}")
                    print("提示: 確認 LM Studio 正在運行且模型已載入\n")

            except KeyboardInterrupt:
                print("\n\n👋 收到中斷信號，再見！\n")
                break

            except EOFError:
                print("\n\n👋 再見！\n")
                break


if __name__ == "__main__":
    client = TerminalChatClient()
    client.run()
