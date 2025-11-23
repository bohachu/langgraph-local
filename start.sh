#!/bin/bash

# 啟動 Agentic AI Chat Client

echo "🚀 啟動 Agentic AI Chat..."
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請先安裝 Python"
    exit 1
fi

# 檢查是否已安裝套件
if ! python3 -c "import langgraph" 2>/dev/null; then
    echo "📦 首次執行，安裝相依套件..."
    pip install -r requirements.txt
    echo ""
fi

# 檢查 LM Studio
echo "🔍 檢查 LM Studio 連線..."
if curl -s http://localhost:1234/v1/models > /dev/null; then
    echo "✅ LM Studio 已連線"
else
    echo "⚠️  警告: 無法連接到 LM Studio (http://localhost:1234)"
    echo "   請確認:"
    echo "   1. LM Studio 已啟動"
    echo "   2. 已載入模型 (例如 gemma-3n-e4b-it-mlx)"
    echo "   3. API Server 已開啟"
    echo ""
    echo "是否繼續？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "▶️  啟動 Chat Client..."
echo ""

# 執行 chat client
python3 chat_client.py
