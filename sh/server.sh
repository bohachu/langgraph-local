#!/bin/bash

# LangGraph Agentic AI Server 啟動腳本

set -e  # 遇到錯誤就停止

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 啟動 LangGraph Agentic AI Server"
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
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "📦 首次執行，安裝相依套件..."
    pip3 install -r requirements.txt
    echo ""
fi

# 檢查 LM Studio
echo ""
echo "🔍 檢查 LM Studio 連線..."
if curl -s --max-time 3 http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio 已連線 (http://localhost:1234)"
else
    echo "⚠️  警告: 無法連接到 LM Studio"
    echo ""
    echo "請確認:"
    echo "  1. LM Studio 已啟動"
    echo "  2. 已載入模型 (例如 gemma-3n-e4b-it-mlx)"
    echo "  3. API Server 已開啟（綠色按鈕）"
    echo ""
    echo "是否繼續啟動 Server？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 檢查 Node.js (for MCP servers)
echo ""
echo "🔍 檢查 Node.js (MCP 需要)..."
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "⚠️  警告: 找不到 Node.js"
    echo "   MCP filesystem server 需要 Node.js"
    echo "   請安裝: https://nodejs.org/"
    echo ""
    echo "是否繼續？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 檢查 port 8000 是否已被使用
echo ""
echo "🔍 檢查 port 8000..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8000 已被使用"
    echo ""
    echo "請選擇:"
    echo "  1. 關閉現有服務並繼續"
    echo "  2. 取消"
    read -r choice
    if [[ "$choice" == "1" ]]; then
        echo "正在關閉 port 8000 的服務..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo "已取消"
        exit 1
    fi
else
    echo "✅ Port 8000 可用"
fi

# 顯示啟動資訊
echo ""
echo "===================================="
echo "📡 Server 設定:"
echo "   - 監聽位址: http://0.0.0.0:8000"
echo "   - API 文檔: http://localhost:8000/docs"
echo "   - 健康檢查: http://localhost:8000/health"
echo ""
echo "🛑 停止 Server: 按 Ctrl+C"
echo "===================================="
echo ""

# 啟動 FastAPI Server
echo "▶️  啟動中..."
echo ""

python3 server.py

# 如果 server 停止
echo ""
echo "👋 Server 已停止"
