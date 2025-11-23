#!/bin/bash

# LangGraph Agentic AI Client 啟動腳本

set -e  # 遇到錯誤就停止

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🤖 啟動 LangGraph Agentic AI Client"
echo "===================================="
echo ""

# 切換到專案目錄
cd "$PROJECT_DIR"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請先安裝 Python"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# 檢查並安裝套件
if ! python3 -c "import httpx" 2>/dev/null; then
    echo ""
    echo "📦 首次執行，安裝相依套件..."
    pip3 install -r requirements.txt
    echo ""
fi

# 從參數或環境變數取得 server URL
SERVER_URL="${1:-${AGENT_SERVER_URL:-http://localhost:8000}}"

echo ""
echo "🔍 檢查 Server 連線..."
echo "   Server URL: $SERVER_URL"

# 檢查 Server 是否運行
if curl -s --max-time 3 "$SERVER_URL/health" > /dev/null 2>&1; then
    echo "✅ Server 已連線"
else
    echo "❌ 無法連接到 Server"
    echo ""
    echo "請確認:"
    echo "  1. Server 已啟動"
    echo "     啟動指令: ./sh/server.sh"
    echo ""
    echo "  2. Server URL 正確"
    echo "     目前設定: $SERVER_URL"
    echo "     修改方式: ./sh/client.sh http://your-server:8000"
    echo ""
    echo "是否繼續？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 顯示啟動資訊
echo ""
echo "===================================="
echo "📡 Client 設定:"
echo "   - Server: $SERVER_URL"
echo "   - API 文檔: $SERVER_URL/docs"
echo ""
echo "可用指令:"
echo "   /help     - 顯示幫助"
echo "   /status   - 伺服器狀態"
echo "   /tools    - 列出可用工具"
echo "   /history  - 對話歷史"
echo "   /clear    - 清除記憶"
echo "   /exit     - 離開"
echo ""
echo "🛑 離開: 輸入 /exit 或按 Ctrl+C"
echo "===================================="
echo ""

# 啟動 Client
python3 client_remote.py "$SERVER_URL"

echo ""
echo "👋 Client 已關閉"
